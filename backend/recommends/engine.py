"""
추천 엔진 핵심 로직: 임베딩(Gemini), Chroma 벡터 검색, 프로필 기반 리랭크,
Top3 이유 생성까지 오케스트레이션한다.
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

# 관리 명령 등 기존 사용자와 호환을 위해 상수 재노출
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
    """
    Chroma 퍼시스턴트 클라이언트 컬렉션 반환 (없으면 생성).
    """
    return vector_db.get_or_create_collection(COLLECTION_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Gemini text-embedding-004 호출 (순차 반복 호출).
    """
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


def build_embedding_text(policy: Policy, max_chars: int = 3500) -> str:
    """
    임베딩용 텍스트 구성: policy_detail 우선, 부족하면 title/summary 보강.
    """
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
    프로필 기반 메타데이터 필터 → Chroma where로 구성.
    컬렉션 메타데이터와 구조가 맞아야 작동한다.
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
                {"min_age": {"$lte": profile.age}},
                {"max_age": {"$gte": profile.age}},
            ]
        }
        where = {"$and": [where, age_clause]} if where else age_clause

    return where


def search_with_chroma(
    query_text: str,
    profile: Optional[Profile],
    top_k: int = 10,
):
    """
    질의 전처리/확장 → 임베딩 → Chroma 검색 → policy_id·거리 반환.
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
    """
    검색된 policy_id 순서대로 Policy 객체 리스트 반환.
    """
    policies = Policy.objects.filter(id__in=policy_ids)
    policy_map = {p.id: p for p in policies}
    ordered = [policy_map[i] for i in policy_ids if i in policy_map]
    return ordered


def _is_unlimited(val) -> bool:
    """
    '제한없음' 값을 와일드카드로 간주.
    """
    if val is None:
        return False
    if isinstance(val, str):
        return val.strip() == "제한없음"
    if isinstance(val, (list, tuple, set)):
        return any(_is_unlimited(v) for v in val)
    return False


def profile_match_score(policy: Policy, profile: Optional[Profile]) -> float:
    """
    프로필-정책 매칭 점수(간단 가중치 기반).
    """
    if not profile:
        return 0.0
    score = 0.0

    if profile.region:
        if policy.region_scope == "NATIONWIDE":
            score += 0.3
        if policy.region_sido and policy.region_sido == profile.region:
            score += 0.2
        if policy.applicable_regions and profile.region in policy.applicable_regions:
            score += 5.0

    if profile.employment_status and policy.employment:
        if _is_unlimited(profile.employment_status) or _is_unlimited(policy.employment):
            score += 1.5
        elif profile.employment_status in policy.employment:
            score += 1.5

    if profile.major and policy.major:
        if _is_unlimited(profile.major) or _is_unlimited(policy.major):
            score += 1.0
        elif profile.major in policy.major:
            score += 1.0

    if profile.special_targets and policy.special_target:
        intersect = set(profile.special_targets).intersection(set(policy.special_target))
        if intersect:
            score += 1.0

    return score


def rerank_with_profile(
    policies: List[Policy],
    distances: List[float],
    profile: Optional[Profile],
    weight_profile: float = 0.6,
    weight_similarity: float = 0.4,
) -> List[Policy]:
    """
    벡터 유사도와 프로필 매칭 점수를 하이브리드로 리랭크.
    distance를 similarity로 변환: sim = 1 / (1 + distance)
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


def assign_ux_scores(policies: List[Policy]) -> List[Policy]:
    """
    하이브리드 점수를 0~100 사이 UX 점수로 정규화하여 policy.ux_score에 저장.
    """
    if not policies:
        return policies

    hybrids = [getattr(p, "hybrid_score", 0.0) for p in policies]
    min_s = min(hybrids)
    max_s = max(hybrids)

    def normalize(x: float) -> int:
        if max_s == min_s:
            return 100
        return round((x - min_s) / (max_s - min_s) * 100)

    for policy, h in zip(policies, hybrids):
        policy.ux_score = normalize(h)
    return policies


def select_top3_with_reasons(
    policies: List[Policy],
    profile: Optional[Profile],
    query: str,
) -> List[Dict]:
    """
    Gemini 2.5 Flash Lite로 상위 3개 정책과 추천 이유 생성.
    """
    api_key = _get_gms_key()
    return generate_top3_with_reasons(policies, profile, query, api_key)
