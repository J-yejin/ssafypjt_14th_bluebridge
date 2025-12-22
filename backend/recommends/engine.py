"""
추천 엔진 유틸리티: 임베딩 호출(Gemini), Chroma 벡터 검색, 프로필 기반 where 필터.
실제 임베딩 적재는 별도 오프라인 스크립트에서 수행하고, 여기서는 검색/설명에 집중한다.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
import requests
from chromadb.config import Settings

from django.conf import settings

from policies.models import Policy
from profiles.models import Profile

CHROMA_DIR = Path(__file__).resolve().parent / "chroma_index"
COLLECTION_NAME = "policies"

# Gemini 설정
GEMINI_EMBED_MODEL = "models/text-embedding-004"
GEMINI_EMBED_URL = (
    "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/"
    "v1beta/models/text-embedding-004:embedContent"
)
GEMINI_GEN_URL = (
    "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash-lite:generateContent"
)


class RecommendEngineError(RuntimeError):
    pass


def _get_gms_key() -> str:
    key = os.getenv("GMS_KEY", getattr(settings, "GMS_KEY", None))
    if not key:
        raise RecommendEngineError("GMS_KEY가 설정되지 않았습니다.")
    return key


def get_chroma_collection():
    """
    Chroma 퍼시스턴트 클라이언트/컬렉션을 반환.
    컬렉션이 없으면 생성한다. (메타데이터는 외부 적재 시 활용)
    """
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        return client.create_collection(
            COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Gemini text-embedding-004 호출 (단순 반복 호출).
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
            raise RecommendEngineError("임베딩 값을 받지 못했습니다.")
        embeddings.append(embedding)
    return embeddings


def build_embedding_text(policy: Policy, max_chars: int = 3500) -> str:
    """
    임베딩 대상 텍스트 구성: policy_detail 우선, 부족하면 title/summary 보강.
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
    프로필 기반 메타데이터 필터를 Chroma where로 구성.
    컬렉션 적재 시 메타데이터 키가 일치해야 동작한다.
    """
    if profile is None:
        return {}

    where: Dict = {}
    if profile.region:
        # 전국(NATIONWIDE) 허용 + 특정 시도 매치. Chroma where에서 OR을 표현하려면 $or 사용.
        where = {
            "$or": [
                {"region_scope": "NATIONWIDE"},
                {"region_sido": profile.region},
            ]
        }

    # 나이 범위(min_age <= age <= max_age) 메타 필터
    if profile.age is not None:
        age_clause = {
            "$and": [
                {"$or": [{"min_age": {"$lte": profile.age}}, {"min_age": {"$eq": None}}]},
                {"$or": [{"max_age": {"$gte": profile.age}}, {"max_age": {"$eq": None}}]},
            ]
        }
        if where:
            where = {"$and": [where, age_clause]}
        else:
            where = age_clause

    # 취업 상태
    if profile.employment_status:
        employment_clause = {"employment": {"$contains": profile.employment_status}}
        if where:
            where = {"$and": [where, employment_clause]}
        else:
            where = employment_clause

    # 전공
    if profile.major:
        major_clause = {"major": {"$contains": profile.major}}
        if where:
            where = {"$and": [where, major_clause]}
        else:
            where = major_clause

    return where


def search_with_chroma(
    query_text: str,
    profile: Optional[Profile],
    top_k: int = 10,
):
    """
    쿼리 임베딩 → Chroma 벡터 검색 → policy_id 목록과 점수 반환.
    """
    collection = get_chroma_collection()
    [query_embedding] = embed_texts([query_text])
    where_filter = build_where_filter(profile)

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter if where_filter else None,
    )
    ids = result.get("ids", [[]])[0] if result else []
    scores = result.get("distances", [[]])[0] if result else []

    # ids는 문자열 리스트로 들어올 가능성이 있으니 int로 변환
    policy_ids = [int(x) for x in ids]
    return policy_ids, scores


def fetch_policies_by_ids(policy_ids: List[int]) -> List[Policy]:
    """
    검색된 policy_id 순서를 유지하며 Policy 객체 리스트 반환.
    """
    policies = Policy.objects.filter(id__in=policy_ids)
    policy_map = {p.id: p for p in policies}
    ordered = [policy_map[i] for i in policy_ids if i in policy_map]
    return ordered


def profile_match_score(policy: Policy, profile: Optional[Profile]) -> float:
    """
    프로필/정책 메타 매칭 점수. 간단 가중치 기반.
    """
    if not profile:
        return 0.0
    score = 0.0

    # 지역 매칭
    if profile.region:
        if policy.region_scope == "NATIONWIDE":
            score += 0.3
        if policy.region_sido and policy.region_sido == profile.region:
            score += 0.2
        if policy.applicable_regions and profile.region in policy.applicable_regions:
            score += 5.0

    # 취업 상태
    if profile.employment_status and policy.employment:
        if profile.employment_status in policy.employment:
            score += 1.5

    # 전공
    if profile.major and policy.major:
        if profile.major in policy.major:
            score += 1.0

    # 특수 대상 교집합
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
        scored.append((hybrid, policy))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


def select_top3_with_reasons(
    policies: List[Policy],
    profile: Optional[Profile],
    query: str,
) -> List[Dict]:
    """
    Gemini 2.5 Flash Lite로 상위 정책 중 3개를 선택하고 간단한 이유(2줄 이내) 생성.
    """
    if not policies:
        return []

    api_key = _get_gms_key()
    url = f"{GEMINI_GEN_URL}?key={api_key}"
    headers = {"Content-Type": "application/json"}

    profile_desc = []
    if profile:
        if profile.region:
            profile_desc.append(f"지역: {profile.region}")
        if profile.age is not None:
            profile_desc.append(f"나이: {profile.age}")
        if profile.employment_status:
            profile_desc.append(f"취업상태: {profile.employment_status}")
        if profile.major:
            profile_desc.append(f"전공: {profile.major}")
        if profile.special_targets:
            profile_desc.append(f"특수대상: {', '.join(profile.special_targets)}")
    profile_str = "; ".join(profile_desc) if profile_desc else "정보 없음"

    items = []
    for p in policies:
        items.append(
            f"- id:{p.id}, 제목:{p.title}, 요약:{(p.summary or p.search_summary or '')[:200]}"
        )
    candidates_str = "\n".join(items)

    prompt = (
        "다음 사용자의 질의와 프로필에 맞춰 후보 정책 중 가장 적합한 3개를 골라주세요.\n"
        "각 결과는 JSON 객체 리스트로 반환하며, 필드는 id와 reason 두 가지만 사용합니다.\n"
        "reason은 한국어로 2줄 이내로 간단히 왜 맞는지 설명하세요.\n\n"
        f"사용자 질의: {query}\n"
        f"프로필: {profile_str}\n"
        "후보 정책:\n"
        f"{candidates_str}\n\n"
        "출력 형식 예시: [{\"id\": 1, \"reason\": \"...\"}, {\"id\":2, \"reason\":\"...\"}, {\"id\":3, \"reason\":\"...\"}]"
    )

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}],
            }
        ]
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # 응답 파싱
    candidates: List[Dict] = []
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        import json  # 지연 import

        candidates = json.loads(text)
    except Exception:
        # 파싱 실패 시 빈 리스트 반환
        candidates = []

    # id가 실제 후보에 있는지 필터
    valid_ids = {p.id for p in policies}
    filtered = []
    for item in candidates:
        pid = item.get("id")
        reason = item.get("reason")
        if pid in valid_ids and reason:
            filtered.append({"id": pid, "reason": reason})
        if len(filtered) >= 3:
            break
    return filtered
