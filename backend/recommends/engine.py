import os
from typing import Dict, List, Optional, Set

import math
import re
import requests
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Lower

from policies.models import Policy
from profiles.models import Profile
from policies.services.explanation_ai import generate_top3_with_reasons
from policies.services.normalize_ai import normalize_query
from policies.services.query_expand_ai import expand_query, expand_query_with_llm
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


def _norm(val):
    """
    Normalize scalar values to align with Chroma metadata rules.
    """
    if val is None:
        return None
    return str(val).strip().lower()


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


def build_embedding_text(policy: Policy) -> str:
    """
    임베딩은 '누구에게 어떤 지원을 하는 정책인가'에 집중: search_summary 중심, title 보조, detail은 짧게.
    """
    texts = []

    # 1) 최우선: search_summary
    if getattr(policy, "search_summary", None):
        texts.append(policy.search_summary.strip())

    # 2) title 보조
    if policy.title:
        texts.append(policy.title.strip())

    # 3) detail은 아주 짧게만
    if policy.policy_detail:
        texts.append(policy.policy_detail[:300].strip())

    return " ".join(texts)


def build_where_filter(profile: Optional[Profile]) -> Dict:
    """
    Use lightweight filter focused on region only.
    Other profile signals move to scoring to avoid over-filtering.
    """
    if profile is None:
        return {}

    profile_region_scope = _norm(getattr(profile, "region_scope", None))
    profile_sido = _norm(getattr(profile, "region_sido", None) or getattr(profile, "region", None))

    where_filter: Dict = {}

    # region_scope
    if profile_region_scope:
        where_filter["region_scope"] = profile_region_scope

    # region_sido (LOCAL 정책일 때)
    if profile_region_scope == "local" and profile_sido:
        where_filter["$or"] = [
            {"region_sido": profile_sido},
            {"applicable_regions": {"$contains": profile_sido}},
        ]

    return where_filter


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
    RAG search: normalize -> LLM 확장 -> embed -> Chroma query.
    Fallbacks: (1) drop where filter, (2) DB LIKE search.
    """
    normalized = normalize_query(query_text)
    llm_expanded = expand_query_with_llm(normalized)
    expanded_query = llm_expanded.get("expanded_query", normalized) or normalized
    query_filters = llm_expanded.get("filters", {}) or {}
    query_categories = set(_norm_list(query_filters.get("category", [])))
    query_employment = set(_norm_list(query_filters.get("employment", [])))

    expanded_list = expand_query(expanded_query)
    combined_query = " ".join(expanded_list) if expanded_list else expanded_query

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

    return policy_ids, scores, combined_query, query_categories, query_employment


def fetch_policies_by_ids(policy_ids: List[int]) -> List[Policy]:
    policies = Policy.objects.filter(id__in=policy_ids)
    policy_map = {p.id: p for p in policies}
    ordered = [policy_map[i] for i in policy_ids if i in policy_map]
    return ordered


def _safe_list(val) -> List[str]:
    if not val:
        return []
    if isinstance(val, (list, tuple, set)):
        return list(val)
    return [val]


def _norm_list(val) -> List[str]:
    return [v for v in (_norm(x) for x in _safe_list(val)) if v]


def _tokenize_query(text: str) -> List[str]:
    if not text:
        return []
    tokens = []
    for part in re.split("[\\s\\|,;/]+", text.lower()):
        t = part.strip()
        if t:
            tokens.append(t)
    return tokens


def intent_score(
    policy: Policy,
    query_tokens: List[str],
    query_categories: Optional[Set[str]] = None,
    query_employment: Optional[Set[str]] = None,
) -> float:
    if not query_tokens and not query_categories and not query_employment:
        return 0.0
    tokens_set = set(query_tokens or [])
    if query_categories:
        tokens_set.update(_norm_list(list(query_categories)))
    if query_employment:
        tokens_set.update(_norm_list(list(query_employment)))
    score = 0.0
    category = _norm(getattr(policy, "category", None))
    if category and category in tokens_set:
        score += 0.6
    keywords = _norm_list(getattr(policy, "keywords", []))
    if keywords:
        matched = sum(1 for k in keywords if k in tokens_set)
        score += min(0.4, matched * 0.1)
    return min(score, 1.0)


def eligibility_score(policy: Policy, profile: Optional[Profile]) -> float:
    """
    Soft eligibility check with region scope/sido.
    """
    if not profile:
        return 1.0
    score = 1.0
    policy_region_scope = _norm(getattr(policy, "region_scope", None))
    profile_sido = _norm(getattr(profile, "region_sido", None) or getattr(profile, "region", None))

    if policy_region_scope == "local" and profile_sido:
        applicable = set(_norm_list(getattr(policy, "applicable_regions", None)))
        if applicable and profile_sido not in applicable:
            score -= 0.3

    return max(score, 0.0)


def build_reason(score_log: Dict[str, float]) -> str:
    """
    규칙 기반 추천 이유 생성 (LLM 없이 사용).
    """
    semantic = score_log.get("semantic", 0.0)
    intent = score_log.get("intent", 0.0)
    eligibility = score_log.get("eligibility", 0.0)

    if intent >= 0.9:
        return "입력하신 관심 분야와 가장 잘 맞는 정책이에요."
    if eligibility < 0.7:
        return "조건은 일부만 충족하지만 참고할 만한 정책이에요."
    if semantic >= 0.8:
        return "정책 설명과 목적이 현재 상황과 잘 맞아요."
    return "전반적인 조건과 정책 목적이 균형 있게 맞아요."


def apply_diversity(policies: List[Policy], max_per_category: int = 2) -> List[Policy]:
    """
    Limit the number of recommendations per category to avoid over-clustering.
    """
    bucket: Dict[str, int] = {}
    final: List[Policy] = []
    for policy in policies:
        cat = _norm(getattr(policy, "category", None)) or "etc"
        count = bucket.get(cat, 0)
        if count >= max_per_category:
            continue
        bucket[cat] = count + 1
        final.append(policy)
    return final

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


def _special_target_match(policy_targets: List[str], profile_targets: List[str]) -> bool:
    """
    Hard cut: 정책 특수대상이 있으면 프로필도 해당 대상이 있어야 통과.
    """
    policy_set = set(_norm_list(policy_targets))
    profile_set = set(_norm_list(profile_targets))
    if not policy_set:
        return True
    if not profile_set:
        return False
    return bool(policy_set.intersection(profile_set))


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

    profile_region_scope = _norm(getattr(profile, "region_scope", None))
    profile_sido = _norm(getattr(profile, "region_sido", None) or getattr(profile, "region", None))
    profile_employment_status = _norm(getattr(profile, "employment_status", None))
    profile_major = _norm(getattr(profile, "major", None))
    profile_special_targets = _norm_list(getattr(profile, "special_targets", None))
    profile_income_quintile = _norm(getattr(profile, "income_quintile", None))
    profile_education_level = _norm(getattr(profile, "education_level", None))
    profile_interest = _norm(getattr(profile, "interest", None))

    policy_region_scope = _norm(getattr(policy, "region_scope", None))
    policy_region_sido = _norm(getattr(policy, "region_sido", None))

    # region weight reduced
    if profile_region_scope or profile_sido:
        if policy_region_scope == "nationwide":
            score += 0.2
        if policy_region_sido and profile_sido and policy_region_sido == profile_sido:
            score += 0.5
        if getattr(policy, "applicable_regions", None):
            try:
                normalized_regions = {
                    r for r in (_norm(r) for r in getattr(policy, "applicable_regions", [])) if r
                }
                if profile_sido and profile_sido in normalized_regions:
                    score += 0.8
            except Exception:
                pass

    # employment / major / special target
    policy_employment = set(_norm_list(policy.employment))
    if profile_employment_status and policy_employment and profile_employment_status in policy_employment:
        score += 0.6

    policy_major = set(_norm_list(policy.major))
    if profile_major and policy_major and profile_major in policy_major:
        score += 0.8

    policy_special_targets = set(_norm_list(policy.special_target))
    profile_special_targets_set = set(profile_special_targets)
    if profile_special_targets_set and policy_special_targets:
        intersect = policy_special_targets.intersection(profile_special_targets_set)
        if intersect:
            score += 0.8
        elif _requires_policy_target(list(policy_special_targets)):
            penalties += 1.0
    # 정책에 강제 매칭 특수대상이 있는데 프로필에 없음 -> 패널티
    if policy_special_targets and not profile_special_targets_set:
        if _requires_policy_target(list(policy_special_targets)):
            penalties += 0.8

    # income_quintile / education_level 일부 반영
    if profile_income_quintile and policy_special_targets:
        if profile_income_quintile in policy_special_targets:
            score += 0.3
    policy_education = set(_norm_list(policy.education))
    if profile_education_level and policy_education and profile_education_level in policy_education:
        score += 0.4

    # interest -> keywords/service_type match
    if profile_interest:
        keywords = _norm_list(getattr(policy, "keywords", []))
        category = _norm(getattr(policy, "category", None))
        if any(profile_interest in k for k in keywords):
            score += 1.0
        if category and profile_interest in category:
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
    query_tokens: Optional[List[str]] = None,
    query_categories: Optional[Set[str]] = None,
    query_employment: Optional[Set[str]] = None,
    weight_profile: float = 0.4,
    weight_similarity: float = 0.6,
) -> List[Policy]:
    """Hybrid rerank with higher emphasis on query similarity."""
    scored = []
    q_tokens = query_tokens or []
    for policy, dist in zip(policies, distances):
        # 정책 대상(강제 필터) 불일치 시 제외 (하드 컷)
        policy_targets = set(_norm_list(getattr(policy, "special_target", [])))
        profile_targets = set(_norm_list(getattr(profile, "special_targets", None))) if profile else set()
        policy.policy_target_required = bool(policy_targets)
        policy.policy_target_match = _special_target_match(list(policy_targets), list(profile_targets))
        if not policy.policy_target_match:
            continue

        # 성별 지정 정책인데 프로필 성별 불일치 -> 제외
        profile_gender = _norm(getattr(profile, "gender", None)) if profile else None
        if profile and _gender_mismatch(list(policy_targets), profile_gender):
            continue

        semantic = 1.0 - dist if dist is not None else 0.0
        semantic = max(0.0, min(1.0, semantic))
        intent = intent_score(policy, q_tokens, query_categories, query_employment)
        eligibility = eligibility_score(policy, profile)

        final_score = (0.5 * semantic) + (0.3 * intent) + (0.2 * eligibility)

        policy.score_components = {
            "semantic": semantic,
            "intent": intent,
            "eligibility": eligibility,
        }
        policy.similarity_score_10 = _to_score_10(semantic, 1.0)
        policy.profile_score_10 = _to_score_10(eligibility, 1.0)
        policy.query_similarity = semantic
        policy.profile_score = eligibility
        policy.hybrid_score = final_score
        scored.append((final_score, policy))

    scored.sort(key=lambda x: x[0], reverse=True)
    ordered = [p for _, p in scored]
    diversified = apply_diversity(ordered)
    return diversified


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
