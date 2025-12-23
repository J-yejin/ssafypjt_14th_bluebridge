import re
from typing import Optional

PUNCT_PATTERN = re.compile(r"[^\w\s]+", re.UNICODE)


def normalize_query(text: Optional[str]) -> str:
    """
    검색 질의 정규화:
    - None/빈값 방어
    - 특수문자 제거
    - 공백 축소
    """
    if not text:
        return ""
    cleaned = PUNCT_PATTERN.sub(" ", text)
    collapsed = re.sub(r"\s+", " ", cleaned)
    return collapsed.strip()
