import json
import re
from typing import Dict, List, Optional

import requests

from policies.models import Policy
from profiles.models import Profile

GEMINI_GEN_URL = (
    "https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash-lite:generateContent"
)


def _parse_json_candidates(text: str) -> List[Dict]:
    """
    모델 응답에서 JSON 리스트만 추출. 실패 시 빈 리스트.
    """
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return []
    return []


def generate_top3_with_reasons(
    policies: List[Policy],
    profile: Optional[Profile],
    query: str,
    api_key: str,
) -> List[Dict]:
    """
    Gemini 2.5 Flash Lite로 3개 추천 + 이유 생성.
    """
    if not policies:
        return []

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
        summary = (p.summary or p.search_summary or "")[:200]
        items.append(f"- id:{p.id}, 제목:{p.title}, 요약:{summary}")
    candidates_str = "\n".join(items)

    prompt = (
        "사용자의 질의와 프로필에 맞는 정책 정보 중 최적의 3개를 골라주세요.\n"
        "- 같은 카테고리만 반복하지 말고 다양하게 선정\n"
        "- 지역/나이/취업/전공/특수대상/요청 키워드 중 일치 항목을 이유에 명시\n"
        "- reason은 한국어 4문장 이내, 상세한 내용을 간결히 표현\n"
        "- JSON만 반환, 각 객체는 id(숫자), reason(문자열) 포함\n\n"
        f"사용자 질의: {query}\n"
        f"사용자 프로필: {profile_str}\n"
        f"정책 정보:\n{candidates_str}\n\n"
        '출력 예시: [{"id": 1, "reason": "..."}]'
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

    candidates: List[Dict] = []
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        candidates = _parse_json_candidates(text)
    except Exception:
        candidates = []

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
