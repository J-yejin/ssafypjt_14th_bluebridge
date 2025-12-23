"""
추천 엔진 로직: 텍스트 임베딩 + 프로필/쿼리 하이브리드 랭킹.
Top3 이유는 Gemini로 생성.
"""

import os
from typing import Dict, List, Optional

import requests
from django.conf import settings

from policies.models import Policy
from profiles.models import Profile
from policies.services.explanation_ai import generate_top3_with_reasons
from policies.services.normalize_ai import normalize_query
from policies.services.query_expand_ai import expand_query
from policies.services import vector_db

# 경로/컬렉션 이름은 policies.services.vector_db와 공유
CHROMA_DIR = vector_db.CHROMA_DIR
COLLECTION_NAME = vector_db.COLLECTION_NAME

# Gemini 설정
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
        raise RecommendEngineError("GMS_KEY가 설정되어 있지 않습니다")
    return key


def get_chroma_collection():
    """Chroma 퍼시스턴트 클라이언트/컬렉션 반환."""
    return vector_db.get_or_create_collection(COLLECTION_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Gemini text-embedding-004 임베딩."""
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
            raise RecommendEngineError("임베딩 값을 받지 못했습니다")
        embeddings.append(embedding)
    return embeddings


def build_embedding_text(policy: Policy, max_chars: int = 1500) -> str:
    """
    임베딩 텍스트 구성(메타 정보 + 핵심 요약, policy_detail 제외):
    - 메타 블록: 카테고리/지원유형/지역/키워드/특수대상
    - 요약 블록: title + summary
    """
    meta_bits = []
    if policy.category:
        meta_bits.append(f"카테고리: {policy.category}")
    if policy.service_type:
        meta_bits.append(f"지원유형: {policy.service_type}")
    if policy.region_scope or policy.region_sido:
        scope = policy.region_scope or ""
        sido = policy.region_sido or ""
        meta_bits.append(f"지역: {scope} {sido}".strip())
    if policy.keywords:
        meta_bits.append(f"키워드: {', '.join(map(str, policy.keywords))}")
    special = policy.special_target or []
    target_detail = policy.target_detail or []
    if special or target_detail:
        combined = special or target_detail
        meta_bits.append(f"대상: {', '.join(map(str, combined))}")

    parts = []
    if meta_bits:
        parts.append(" | ".join(meta_bits))
    if policy.title:
        parts.append(policy.title)
    if policy.summary:
        parts.append(policy.summary)

    text = "\n".join([p for p in parts if p])
    return text[:max_chars]


def _profile_interests(profile: Optional[Profile]) -> List[str]:
    if not profile or not profile.interest:
        return []
    return [t.strip().lower() for t in profile.interest.split(",") if t.strip()]


def build_where_filter(profile: Optional[Profile]) -> Dict:
    """
    프로필 기반 메타데이터를 Chroma where에 반영(더 엄격하게 AND 비율 강화).
    """
    if profile is None:
        return {}

    where: Dict = {}
    if profile.region:
        where = {
            "$or": [
                {"region_scope": "NATIONWIDE"},
                {"region_sido": profile.region},
            ]
        }

    if profile.age is not None:
        age_clause = {
            "$and": [
                {"$or": [{"min_age": {"$lte": profile.age}}, {"min_age": {"$eq": None}}]},
                {"$or": [{"max_age": {"$gte": profile.age}}, {"max_age": {"$eq": None}}]},
            ]
        }
        where = {"$and": [where, age_clause]} if where else age_clause

    if profile.employment_status:
        employment_clause = {"employment": {"$contains": profile.employment_status}}
        where = {"$and": [where, employment_clause]} if where else employment_clause

    if profile.major:
        major_clause = {"major": {"$contains": profile.major}}
        where = {"$and": [where, major_clause]} if where else major_clause

    return where


def search_with_chroma(
    query_text: str,
    profile: Optional[Profile],
    top_k: int = 30,
):
    """
    질의/프로필 기반으로 Chroma 검색하여 policy_id·거리 반환.
    """
    normalized = normalize_query(query_text)
    expanded_list = expand_query(normalized)
    combined_query = " ".join(expanded_list) if expanded_list else normalized

    collection = get_chroma_collection()
    [query_embedding] = embed_texts([combined_query])
    where_filter = build_where_filter(profile)

    result = vector_db.query(
        query_embeddings=[query_embedding],
        where=where_filter if where_filter else None,
        top_k=top_k,
        name=COLLECTION_NAME,
    )
    ids = result.get("ids", [[]])[0] if result else []
    scores = result.get("distances", [[]])[0] if result else []

    policy_ids = [int(x) for x in ids]
    return policy_ids, scores


def fetch_policies_by_ids(policy_ids: List[int]) -> List[Policy]:
    """검색된 policy_id 순서대로 Policy 객체 리스트 반환."""
    policies = Policy.objects.filter(id__in=policy_ids)
    policy_map = {p.id: p for p in policies}
    ordered = [policy_map[i] for i in policy_ids if i in policy_map]
    return ordered


def profile_match_score(policy: Policy, profile: Optional[Profile]) -> float:
    """
    프로필 적합도 점수(항목별 가중치 반영).
    """
    if not profile:
        return 0.0
    score = 0.0

    # 지역 가중
    if profile.region:
        if policy.region_scope == "NATIONWIDE":
            score += 0.5
        if policy.region_sido and policy.region_sido == profile.region:
            score += 0.5
        if policy.applicable_regions and profile.region in policy.applicable_regions:
            score += 2.5

    # 취업 상태
    if profile.employment_status and policy.employment:
        if profile.employment_status in policy.employment:
            score += 2.0

    # 전공
    if profile.major and policy.major:
        if profile.major in policy.major:
            score += 1.0

    # 특수대상
    if profile.special_targets and policy.special_target:
        intersect = set(profile.special_targets).intersection(set(policy.special_target))
        if intersect:
            score += 1.5

    # 관심사 키워드 매칭(보너스)
    interests = _profile_interests(profile)
    if interests:
        text_tokens = []
        if policy.keywords:
            text_tokens.extend([str(k).lower() for k in policy.keywords])
        if policy.summary:
            text_tokens.extend(policy.summary.lower().split())
        if any(tok in " ".join(text_tokens) for tok in interests):
            score += 0.8

    return score


def rerank_with_profile(
    policies: List[Policy],
    distances: List[float],
    profile: Optional[Profile],
    weight_profile: float = 0.7,
    weight_similarity: float = 0.3,
) -> List[Policy]:
    """
    벡터 유사도와 프로필 매칭 점수를 결합해 하이브리드 랭킹.
    distance -> similarity: sim = 1 / (1 + distance)
    """
    scored = []
    for policy, dist in zip(policies, distances):
        sim = 1.0 / (1.0 + dist) if dist is not None else 0.0
        pscore = profile_match_score(policy, profile)
        hybrid = weight_profile * pscore + weight_similarity * sim
        # 디버깅/UX 노출용 점수 보관
        policy.profile_score = pscore
        policy.query_similarity = sim
        policy.hybrid_score = hybrid
        scored.append((hybrid, policy))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


def apply_diversity_penalty(policies: List[Policy], alpha: float = 0.1) -> List[Policy]:
    """
    동일 카테고리/기관 반복에 패널티를 주어 다양성 확보.
    """
    if not policies:
        return policies

    category_count: Dict[str, int] = {}
    provider_count: Dict[str, int] = {}
    penalized: List[Policy] = []

    for p in policies:
        cat = (p.category or "").lower()
        prov = (p.provider or "").lower()
        penalty = alpha * (category_count.get(cat, 0) + provider_count.get(prov, 0))
        p.hybrid_score = getattr(p, "hybrid_score", 0.0) - penalty
        category_count[cat] = category_count.get(cat, 0) + 1
        provider_count[prov] = provider_count.get(prov, 0) + 1
        penalized.append(p)

    penalized.sort(key=lambda x: getattr(x, "hybrid_score", 0.0), reverse=True)
    return penalized


def assign_ux_scores(policies: List[Policy]) -> List[Policy]:
    """
    하이브리드 점수를 0~100 UX 점수로 정규화 후 구간화.
    - min==max이면 80으로 고정(과신 방지)
    - 0~20% -> 0~40, 20~60% -> 40~70, 60~100% -> 70~100으로 재매핑
    """
    if not policies:
        return policies

    hybrids = [getattr(p, "hybrid_score", 0.0) for p in policies]
    min_s = min(hybrids)
    max_s = max(hybrids)

    def normalize(x: float) -> int:
        if max_s == min_s:
            return 80
        base = (x - min_s) / (max_s - min_s) * 100
        if base < 20:
            return round(base / 20 * 40)
        if base < 60:
            return round(40 + (base - 20) / 40 * 30)
        return round(70 + (base - 60) / 40 * 30)

    for policy, h in zip(policies, hybrids):
        policy.ux_score = normalize(h)
    return policies


def select_top3_with_reasons(
    policies: List[Policy],
    profile: Optional[Profile],
    query: str,
) -> List[Dict]:
    """
    Gemini 2.5 Flash Lite로 3개 정책 추천 이유 생성.
    """
    api_key = _get_gms_key()
    return generate_top3_with_reasons(policies, profile, query, api_key)
