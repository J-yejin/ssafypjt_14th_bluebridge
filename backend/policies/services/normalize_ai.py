import re
from typing import Optional, Set

PUNCT_PATTERN = re.compile(r"[^\w\s]+", re.UNICODE)
STOPWORDS: Set[str] = {
    "그리고",
    "하지만",
    "그러나",
    "또는",
    "또한",
    "및",
    "에서",
    "으로",
    "에게",
    "까지",
    "부터",
    "이다",
    "에는",
    "하는",
    "하다",
    "관련",
    "대해",
    "대해서",
    "정책",
    "지원",
    "사업",
}


def normalize_query(text: Optional[str]) -> str:
    """
    검색 질의 정규화:
    - None/빈값 방어
    - 특수문자 제거
    - 공백 축소
    - 가벼운 불용어 제거
    """
    if not text:
        return ""
    cleaned = PUNCT_PATTERN.sub(" ", text)
    collapsed = re.sub(r"\s+", " ", cleaned).strip()
    tokens = [tok for tok in collapsed.split(" ") if tok and tok not in STOPWORDS]
    return " ".join(tokens)
