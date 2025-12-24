from typing import List, Optional, Set


SYNONYM_MAP = {
    "일자리": ["일자리", "취업", "창업", "근로", "고용", "창직"],
    "교육": ["교육", "훈련", "강의", "연수"],
    "복지/문화": ["복지", "문화", "여가", "체육", "생활"],
    "건강": ["건강", "보건", "의료"],
    "생활지원": ["생활지원", "주거", "주택", "주거비", "생활안정"],
    "재무/법률": ["재무", "법률", "서민금융", "금융", "신용", "대출", "융자", "채무"],
    "위기·안전": ["위기", "안전", "재난", "재해", "치안"],
    "가족/권리": ["가족", "권리", "육아", "양육", "돌봄"],
    "기타": ["기타"],
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
