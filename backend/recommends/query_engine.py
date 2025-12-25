from typing import List, Optional, Dict, Tuple

from django.contrib.auth.models import User

from .services.query_normalize_ai import normalize_query_llm
from .services.embedding import embed_texts
from .services.policy_index import load_index
from .reason.query_reason_ai import build_query_reason_ai
from .reason.query_reason import build_query_reason

# 간단 지역 키워드 목록 (시/도 기준)
REGION_KEYWORDS = {
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
}


def _score_candidate(item: Dict, keywords: List[str]) -> float:
    """
    간단 키워드 매칭 점수.
    """
    if not keywords:
        return 0.0
    text = " ".join(
        [
            item.get("title") or "",
            item.get("search_summary") or "",
            item.get("summary") or "",
            item.get("category") or "",
        ]
    ).lower()
    score = 0
    for kw in keywords:
        if kw and kw.lower() in text:
            score += 1
    return float(score)


def _cosine_sim(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def query_recommend(query: str, user: Optional[User] = None) -> List[dict]:
    """
    JSON 인덱스 기반: LLM 정규화 → 키워드 필터로 후보 30개 → 임베딩 유사도 top4 → LLM 이유.
    """
    normalized = normalize_query_llm(query)
    intent = normalized.get("intent") or query
    keywords = normalized.get("keywords") or []
    tokens = intent.split() + query.split()
    terms = [t for t in keywords + tokens if t]

    # 지역 키워드 추출
    region_terms = {t for t in terms for r in REGION_KEYWORDS if r in t}
    has_region_filter = bool(region_terms)

    index = load_index()
    if not index:
        return []

    # 1) 키워드 매칭 후보 선별 (최소 1개 이상 매칭)
    scored: List[Tuple[float, Dict]] = []
    for item in index:
        if has_region_filter:
            region_match = False
            item_region = (item.get("region_sido") or "").lower()
            item_regions = [str(r).lower() for r in (item.get("applicable_regions") or [])]
            for rt in region_terms:
                lrt = rt.lower()
                if lrt in item_region or any(lrt in r for r in item_regions) or item.get("region_scope") == "NATIONWIDE":
                    region_match = True
                    break
            if not region_match:
                continue
        score = _score_candidate(item, terms)
        if score <= 0:
            continue
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    candidates = [item for _, item in scored[:30]] if scored else []
    if not candidates:
        return []

    # 2) 임베딩 재랭크 (search_summary 우선, fallback summary/title)
    texts = [
        (c.get("search_summary") or c.get("summary") or c.get("title") or "")[:400] for c in candidates
    ]
    try:
        query_vec = embed_texts([intent])[0]
        doc_vecs = embed_texts(texts)
        sims = [(_cosine_sim(query_vec, dv), c) for dv, c in zip(doc_vecs, candidates)]
        sims.sort(key=lambda x: x[0], reverse=True)
        top_items = [c for _, c in sims[:4]]
    except Exception:
        top_items = candidates[:4]

    results = []
    for item in top_items:
        ai_reason = build_query_reason_ai(item, query, summary=item.get("search_summary") or item.get("summary"))
        fallback = build_query_reason(item, query)
        results.append(
            {
                "policy_id": item["id"],
                "title": item.get("title"),
                "category": item.get("category"),
                "reason": ai_reason or fallback,
            }
        )
    return results
