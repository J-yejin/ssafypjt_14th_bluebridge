import os
from typing import Dict, List, Optional

import math
import requests
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Lower

from policies.models import Policy
from profiles.models import Profile
from policies.services.explanation_ai import generate_top3_with_reasons
from policies.services.normalize_ai import normalize_query
from policies.services.query_expand_ai import expand_query
from policies.services import vector_db

# collection config
CHROMA_DIR = vector_db.CHROMA_DIR
COLLECTION_NAME = vector_db.COLLECTION_NAME

# Gemini config
GEMINI_EMBED_MODEL = "models/text-embedding-004"
GEMINI_EMBED_URL = (
    "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/"
    "v1beta/models/text-embedding-004:embedContent"
)


class RecommendEngineError(RuntimeError):
    pass


def _get_gms_key() -> str:
    key = os.getenv("GMS_KEY", getattr(settings, "GMS_KEY", None))
    if not key:
        raise RecommendEngineError("GMS_KEY is not configured")
    return key


def get_chroma_collection():
    """Return or create the Chroma collection (cached by Chroma)."""
    return vector_db.get_or_create_collection(COLLECTION_NAME)


def embed_texts(texts: List[str], mode: str = "document") -> List[List[float]]:
    """
    Call Gemini embedding (one-by-one to be safe).
    mode: "document" -> RETRIEVAL_DOCUMENT, "query" -> RETRIEVAL_QUERY (fallback: SEMANTIC_SIMILARITY)
    """
    api_key = _get_gms_key()
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    task_type = "RETRIEVAL_DOCUMENT"
    if mode == "query":
        task_type = "RETRIEVAL_QUERY"

    embeddings: List[List[float]] = []
    for text in texts:
        payload = {
            "model": GEMINI_EMBED_MODEL,
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
        }
        resp = requests.post(GEMINI_EMBED_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        embedding = data.get("embedding", {}).get("values")
        if not embedding:
            raise RecommendEngineError("embedding not returned")
        embeddings.append(embedding)
    return embeddings


def build_embedding_text(policy: Policy, max_chars: int = 3500) -> str:
    """
    임베딩 입력을 summary 중심으로 구성하고 title은 보조로 둡니다.
    """
    parts = []
    if policy.summary:
        parts.append(policy.summary)
    if policy.title:
        parts.append(policy.title)
    if policy.policy_detail:
        parts.append(policy.policy_detail)
    text = "\n".join([p for p in parts if p])
    return text[:max_chars]


def build_where_filter(profile: Optional[Profile]) -> Dict:
    """
    Use lightweight filter focused on region only.
    Other profile signals move to scoring to avoid over-filtering.
    """
    if profile is None or not profile.region:
        return {}

    return {
        "$or": [
            {"region_scope": "nationwide"},
            {"region_sido": profile.region.lower()},
        ]
    }


def _fallback_db_search(query_text: str, limit: int = 10) -> List[Policy]:
    """SQLite-safe LIKE search on title/search_summary (lowered)."""
    if not query_text:
        return []
    q = query_text.lower()
    qs = (
        Policy.objects.filter(status="ACTIVE")
        .annotate(
            lower_title=Lower("title"),
            lower_summary=Lower("search_summary"),
        )
        .filter(Q(lower_title__contains=q) | Q(lower_summary__contains=q))
        .order_by("end_date")[:limit]
    )
    return list(qs)


def search_with_chroma(
    query_text: str,
    profile: Optional[Profile],
    top_k: int = 10,
):
    """
    RAG search: normalize/expand -> embed -> Chroma query.
    Fallbacks: (1) drop where filter, (2) DB LIKE search.
    """
    normalized = normalize_query(query_text)
    expanded_list = expand_query(normalized)
    combined_query = " ".join(expanded_list) if expanded_list else normalized

    where_filter = build_where_filter(profile)

    def _chroma_query(where=None):
        try:
            [query_embedding] = embed_texts([combined_query], mode="query")
            result = vector_db.query(
                query_embeddings=[query_embedding],
                where=where if where else None,
                top_k=top_k,
                name=COLLECTION_NAME,
            )
            ids = result.get("ids", [[]])[0] if result else []
            scores = result.get("distances", [[]])[0] if result else []
            return [int(x) for x in ids], scores
        except Exception:
            return [], []

    policy_ids, scores = _chroma_query(where_filter if where_filter else None)

    if not policy_ids and where_filter:
        # retry without where filter
        policy_ids, scores = _chroma_query(None)

    if not policy_ids:
        fallback_policies = _fallback_db_search(normalized, limit=top_k)
        policy_ids = [p.id for p in fallback_policies]
        scores = [0.0 for _ in policy_ids]

    return policy_ids, scores


def fetch_policies_by_ids(policy_ids: List[int]) -> List[Policy]:
    policies = Policy.objects.filter(id__in=policy_ids)
    policy_map = {p.id: p for p in policies}
    ordered = [policy_map[i] for i in policy_ids if i in policy_map]
    return ordered


def _safe_list(val) -> List[str]:
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [val]

# 정책 대상(강제 필터링) 키워드 목록
POLICY_TARGET_FORCE_KEYS = {
    "국가유공자",
    "장애인", "장애",
    "보훈가족", "보훈대상자", "보훈",
    "한부모가정", "한부모·조손",
    "저소득층", "저소득","기초생활수급자"
    "다자녀",
    "군인",
    "농업인",
    "다문화·탈북민",
    "여성",
    "한부모·조손"
}

# 프로필 점수를 0~10으로 변환할 때 사용할 기준값 (가산치 합이 5 내외이므로 5를 상한으로 사용)
PROFILE_SCORE_MAX = 5.0
GENDER_KEYWORDS = {
    "male": {"남성", "남자"},
    "female": {"여성", "여자"},
}


def _requires_policy_target(targets: List[str]) -> bool:
    """
    정책의 특수대상(정책 대상) 목록에 강제 매칭이 필요한 키워드가 포함되면 True.
    """
    lowered = [str(t).strip().lower() for t in targets or []]
    for key in POLICY_TARGET_FORCE_KEYS:
        lkey = key.lower()
        if any(lkey in t for t in lowered):
            return True
    return False


def _gender_mismatch(policy_targets: List[str], profile_gender: Optional[str]) -> bool:
    """
    정책 특수대상에 성별 키워드가 있으면 프로필 성별과 불일치 시 True.
    프로필 성별이 없으면 성별 지정 정책은 제외.
    """
    if not policy_targets:
        return False
    lowered = {str(t).strip().lower() for t in policy_targets}
    for g, keys in GENDER_KEYWORDS.items():
        if any(k in lowered for k in keys):
            if not profile_gender:
                return True
            return profile_gender.lower() != g
    return False


def profile_match_score(policy: Policy, profile: Optional[Profile]) -> float:
    """Simpler weighted scoring focusing on profile signals (lower weight than query)."""
    if not profile:
        return 0.0
    score = 0.0
    penalties = 0.0

    # region weight reduced
    if profile.region:
        if policy.region_scope and policy.region_scope.upper() == "NATIONWIDE":
            score += 0.2
        if policy.region_sido and policy.region_sido.lower() == profile.region.lower():
            score += 0.5
        if getattr(policy, "applicable_regions", None):
            try:
                if profile.region in policy.applicable_regions:
                    score += 0.8
            except Exception:
                pass

    # employment / major / special target
    if profile.employment_status and policy.employment:
        if profile.employment_status in _safe_list(policy.employment):
            score += 0.6

    if profile.major and policy.major:
        if profile.major in _safe_list(policy.major):
            score += 0.8

    if profile.special_targets and policy.special_target:
        intersect = set(profile.special_targets).intersection(set(_safe_list(policy.special_target)))
        if intersect:
            score += 0.8
        elif _requires_policy_target(_safe_list(policy.special_target)):
            penalties += 1.0
    # 정책에 강제 매칭 특수대상이 있는데 프로필에 없음 -> 패널티
    if policy.special_target and not profile.special_targets:
        if _requires_policy_target(_safe_list(policy.special_target)):
            penalties += 0.8

    # income_quintile / education_level 일부 반영
    if profile.income_quintile and policy.special_target:
        if profile.income_quintile in _safe_list(policy.special_target):
            score += 0.3
    if profile.education_level and policy.education:
        if profile.education_level in _safe_list(policy.education):
            score += 0.4

    # interest -> keywords/service_type match
    if profile.interest:
        keywords = _safe_list(getattr(policy, "keywords", []))
        category = getattr(policy, "category", None)
        if any(profile.interest in str(k) for k in keywords):
            score += 1.0
        if category and profile.interest in str(category):
            score += 0.6

    # age soft check
    if profile.age is not None:
        try:
            if policy.min_age and profile.age < policy.min_age:
                penalties += 0.3
            if policy.max_age and profile.age > policy.max_age:
                penalties += 0.3
        except Exception:
            pass

    return score - penalties


def _to_score_10(value: float, max_value: float = 1.0) -> float:
    """Clamp and scale any metric to 0~10."""
    if max_value <= 0:
        return 0.0
    scaled = (value / max_value) * 10.0
    return round(max(0.0, min(10.0, scaled)), 1)


def rerank_with_profile(
    policies: List[Policy],
    distances: List[float],
    profile: Optional[Profile],
    weight_profile: float = 0.4,
    weight_similarity: float = 0.6,
) -> List[Policy]:
    """Hybrid rerank with higher emphasis on query similarity."""
    scored = []
    for policy, dist in zip(policies, distances):
        # 정책 대상(강제 필터) 불일치 시 제외
        policy_targets = {str(t).strip().lower() for t in _safe_list(getattr(policy, "special_target", []))}
        requires_match = _requires_policy_target(policy_targets)
        policy.policy_target_required = requires_match
        policy.policy_target_match = None

        if requires_match:
            if not profile or not getattr(profile, "special_targets", None):
                policy.policy_target_match = False
                continue
            profile_targets = {str(t).strip().lower() for t in (profile.special_targets or [])}
            intersects = policy_targets.intersection(profile_targets)
            policy.policy_target_match = bool(intersects)
            if not policy.policy_target_match:
                continue
        else:
            policy.policy_target_match = True

        # 성별 지정 정책인데 프로필 성별 불일치 -> 제외
        if profile and _gender_mismatch(list(policy_targets), getattr(profile, "gender", None)):
            continue

        sim = 1.0 / (1.0 + dist) if dist is not None else 0.0
        pscore = profile_match_score(policy, profile)

        policy.similarity_score_10 = _to_score_10(sim, 1.0)
        policy.profile_score_10 = _to_score_10(max(pscore, 0.0), PROFILE_SCORE_MAX)
        hybrid = weight_profile * pscore + weight_similarity * sim
        policy.profile_score = pscore
        policy.query_similarity = sim
        policy.hybrid_score = hybrid
        scored.append((hybrid, policy))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


def assign_ux_scores(policies: List[Policy]) -> List[Policy]:
    """
    Map hybrid_score to 0-100 UX score using softmax for 안정적 분포.
    """
    if not policies:
        return policies

    hybrids = [float(getattr(p, "hybrid_score", 0.0)) for p in policies]
    max_h = max(hybrids)
    exp_scores = [math.exp(h - max_h) for h in hybrids]
    denom = sum(exp_scores)

    if denom == 0:
        for policy in policies:
            policy.ux_score = 50
        return policies

    for policy, exp_s in zip(policies, exp_scores):
        policy.ux_score = round((exp_s / denom) * 100)
    return policies


def select_top3_with_reasons(
    policies: List[Policy],
    profile: Optional[Profile],
    query: str,
) -> List[Dict]:
    api_key = _get_gms_key()
    return generate_top3_with_reasons(policies, profile, query, api_key)
