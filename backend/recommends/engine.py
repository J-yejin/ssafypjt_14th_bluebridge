import os
from typing import Dict, List, Optional

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


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Call Gemini embedding (one-by-one to be safe)."""
    api_key = _get_gms_key()
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    embeddings: List[List[float]] = []
    for text in texts:
        payload = {
            "model": GEMINI_EMBED_MODEL,
            "content": {"parts": [{"text": text}]},
            "taskType": "RETRIEVAL_DOCUMENT",
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
    parts = []
    if policy.title:
        parts.append(policy.title)
    if policy.summary:
        parts.append(policy.summary)
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
            collection = get_chroma_collection()
            [query_embedding] = embed_texts([combined_query])
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

# 특수대상 중 매칭을 강제할 키워드
FORCE_SPECIAL_TARGET_KEYS = {
    "장애",
    "장애인",
    "보훈",
    "보훈대상자",
    "국가유공자",
    "국가 유공자",
    "저소득",
    "저소득층",
    "한부모",
    "차상위",
    "생계급여",
    "기초생활",
}


def _requires_special_match(targets: List[str]) -> bool:
    """
    정책의 특수대상 목록에 강제 매칭이 필요한 키워드가 포함되면 True.
    """
    lowered = [str(t).lower() for t in targets or []]
    for key in FORCE_SPECIAL_TARGET_KEYS:
        if any(key in t for t in lowered):
            return True
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
            score += 1.2

    if profile.major and policy.major:
        if profile.major in _safe_list(policy.major):
            score += 0.8

    if profile.special_targets and policy.special_target:
        intersect = set(profile.special_targets).intersection(set(_safe_list(policy.special_target)))
        if intersect:
            score += 0.8
        elif _requires_special_match(_safe_list(policy.special_target)):
            penalties += 1.0
    # 정책에 강제 매칭 특수대상이 있는데 프로필에 없음 -> 패널티
    if policy.special_target and not profile.special_targets:
        if _requires_special_match(_safe_list(policy.special_target)):
            penalties += 0.8

    # gender / income_quintile / education_level 일부 반영
    if profile.gender and policy.special_target:
        if profile.gender in _safe_list(policy.special_target):
            score += 0.5
    if profile.income_quintile and policy.special_target:
        if profile.income_quintile in _safe_list(policy.special_target):
            score += 0.3
    if profile.education_level and policy.education:
        if profile.education_level in _safe_list(policy.education):
            score += 0.4

    # interest -> keywords/service_type match
    if profile.interest:
        keywords = _safe_list(getattr(policy, "keywords", []))
        service_type = getattr(policy, "service_type", None)
        if any(profile.interest in str(k) for k in keywords):
            score += 0.6
        if service_type and profile.interest in str(service_type):
            score += 0.4

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
        # 강제 매칭 특수대상 불일치 시 제외
        if profile and policy.special_target:
            requires_match = _requires_special_match(_safe_list(policy.special_target))
            if requires_match:
                intersects = set(_safe_list(policy.special_target)).intersection(set(profile.special_targets or []))
                if not intersects:
                    continue

        sim = 1.0 / (1.0 + dist) if dist is not None else 0.0
        pscore = profile_match_score(policy, profile)
        hybrid = weight_profile * pscore + weight_similarity * sim
        policy.profile_score = pscore
        policy.query_similarity = sim
        policy.hybrid_score = hybrid
        scored.append((hybrid, policy))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


def assign_ux_scores(policies: List[Policy]) -> List[Policy]:
    """Map hybrid_score to 0-100 UX score (flat 50 when all equal)."""
    if not policies:
        return policies

    hybrids = [getattr(p, "hybrid_score", 0.0) for p in policies]
    min_s = min(hybrids)
    max_s = max(hybrids)

    def normalize(x: float) -> int:
        if max_s == min_s:
            return 50
        return round((x - min_s) / (max_s - min_s) * 100)

    for policy, h in zip(policies, hybrids):
        policy.ux_score = normalize(h)
    return policies


def select_top3_with_reasons(
    policies: List[Policy],
    profile: Optional[Profile],
    query: str,
) -> List[Dict]:
    api_key = _get_gms_key()
    return generate_top3_with_reasons(policies, profile, query, api_key)
