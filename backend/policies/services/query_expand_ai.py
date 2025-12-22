from typing import List, Optional, Set


SYNONYM_MAP = {
    "취업": ["일자리", "채용", "고용"],
    "창업": ["스타트업", "사업 시작", "창업지원"],
    "주거": ["전세", "월세", "주택", "집"],
    "교육": ["훈련", "스쿨", "강좌"],
    "금융": ["대출", "융자", "보증"],
    "청년": ["청년층", "청소년", "청년정책"],
}


def expand_query(text: Optional[str]) -> List[str]:
    """
    간단한 룰 기반 질의 확장: 키워드 동의어를 추가해 recall을 보조한다.
    """
    if not text:
        return []

    expanded: List[str] = [text]
    tokens = text.split()
    seen: Set[str] = set(expanded)
    for token in tokens:
        for key, synonyms in SYNONYM_MAP.items():
            if key in token:
                for syn in synonyms:
                    if syn not in seen:
                        expanded.append(syn)
                        seen.add(syn)
    return expanded
