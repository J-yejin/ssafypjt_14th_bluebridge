import json
import os
from typing import Dict, List, Optional, Set

import requests
from django.conf import settings

# 서비스 카테고리 동의어 (Single Source of Truth)
CATEGORY_SYNONYMS: Dict[str, List[str]] = {
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

# 간단한 룰 기반 동의어 확장 (recall 보조)
SYNONYM_MAP = CATEGORY_SYNONYMS

GEMINI_MODEL = "models/gemini-2.5-flash lite"
GEMINI_GENERATE_URL = (
    "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash-lite:generateContent"
)


def _get_gms_key() -> str:
    key = os.getenv("GMS_KEY", getattr(settings, "GMS_KEY", None))
    if not key:
        raise RuntimeError("GMS_KEY is not configured")
    return key


def expand_query(text: Optional[str]) -> List[str]:
    """
    간단한 룰기반 확장: 키워드의 동의어를 추가해 recall을 보조한다.
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


def expand_query_with_llm(user_query: str):
    """
    LLM 기반 쿼리 확장/필터 추출. GMS Gemini Flash 사용.
    """
    prompt = f"""
너는 청년 정책 추천 시스템의 쿼리 분석기다.

사용자 입력을 아래 JSON 형식으로 변환해라.

규칙:
- expanded_query: 정책 검색에 적합한 한 문장 (사용자 의미를 보존하되 정책 검색에 맞게 재서술)
- filters:
  - category: [주거, 일자리, 교육, 금융, 복지, 생활지원, 재무/법률, 위기·안전, 가족/권리, 기타] 중 해당되는 것
  - employment: [미취업자, 재직자] 중 해당되는 것
  - region: 특정 지역이 명시되면 문자열, 아니면 null
  - exclude_keywords: 제외하고 싶은 대상

카테고리는 반드시 우리 서비스 카테고리에서만 선택한다.

JSON 외 텍스트 출력 금지.

사용자 입력:
"{user_query}"
"""

    api_key = _get_gms_key()
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "model": GEMINI_MODEL,
        "contents": [{"parts": [{"text": prompt}]}],
    }
    try:
        resp = requests.post(GEMINI_GENERATE_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        return json.loads(text)
    except Exception:
        return {
            "expanded_query": user_query,
            "filters": {}
        }
