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
    모델 응답에서 JSON 리스트 추출. 실패 시 빈 리스트.
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
    Gemini 2.5 Flash Lite로 상위 3개 추천 + 이유 생성.
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
        if profile.gender:
            profile_desc.append(f"성별: {profile.gender}")
        if profile.employment_status:
            profile_desc.append(f"취업상태: {profile.employment_status}")
        if profile.education_level:
            profile_desc.append(f"학력: {profile.education_level}")
        if profile.major:
            profile_desc.append(f"전공: {profile.major}")
        if profile.income_quintile:
            profile_desc.append(f"소득분위: {profile.income_quintile}")
        if profile.interest:
            profile_desc.append(f"관심사: {profile.interest}")
        if profile.special_targets:
            profile_desc.append(f"특수대상: {', '.join(profile.special_targets)}")
    profile_str = "; ".join(profile_desc) if profile_desc else "정보 없음"

    items = []
    for p in policies:
        summary = (p.summary or p.search_summary or "")[:200]
        sim = getattr(p, "query_similarity", None)
        sim_text = f", 유사도:{sim:.3f}" if sim is not None else ""
        items.append(f"- id:{p.id}, 제목:{p.title}{sim_text}, 요약:{summary}")
    candidates_str = "\n".join(items)

    prompt = (
        "당신은 정책 상담가입니다. 아래 사용자 질의에 가장 직접적으로 관련된 정책 3개를 고르고, "
        "왜 질의에 맞는지 근거를 짧게 설명하세요. 프로필은 보조 신호로만 사용하세요.\n"
        "- JSON 리스트로 반환하며 각 객체는 id, reason을 포함합니다.\n"
        "- reason은 한국어 1~2문장, 180자 이내. 사용자 질의 조건과 정책의 대상/혜택/지역이 어떻게 맞는지 먼저 설명하고, "
        "프로필(지역/나이/성별/취업상태/전공/특수대상/관심사/소득분위/학력)과의 적합성을 보조적으로 언급하세요.\n"
        "- 과장 없이 사실 기반, 빈 reason 금지. 질의와 무관한 정책은 선택하지 않습니다.\n\n"
        f"사용자 질의: {query}\n"
        f"사용자 프로필(참고용): {profile_str}\n"
        f"정책 후보들(유사도 높은 순으로 제공됨):\n{candidates_str}\n\n"
        '출력 예시: [{"id": 1, "reason": "질의의 요구와 이 정책의 지원이 일치, 지역/나이/대상도 충족"}]'
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
            filtered.append({"id": pid, "reason": str(reason)[:180]})
        if len(filtered) >= 3:
            break

    # Fallback: 모델이 reason을 못 주면 간단한 규칙 기반 이유 생성
    if len(filtered) < 3:
        for p in policies:
            if len(filtered) >= 3:
                break
            if p.id in {f["id"] for f in filtered}:
                continue
            # 간단한 근거 생성
            why = []
            if profile and profile.region:
                if p.region_scope == "NATIONWIDE":
                    why.append("전국 대상이라 지역 제약이 없습니다.")
                elif p.region_sido and profile.region in p.region_sido:
                    why.append(f"{profile.region} 거주자가 신청 가능합니다.")
            if profile and profile.age is not None:
                if p.min_age and p.min_age <= profile.age:
                    why.append(f"{profile.age}세가 최소 연령 요건을 충족합니다.")
                if p.max_age and p.max_age >= profile.age:
                    why.append(f"{profile.age}세가 최대 연령 요건을 충족합니다.")
            if profile and profile.employment_status and p.employment:
                if profile.employment_status in p.employment:
                    why.append(f"{profile.employment_status} 대상 정책입니다.")
            if profile and profile.major and p.major:
                if profile.major in p.major:
                    why.append("전공 요건이 맞습니다.")
            if not why:
                why.append("프로필 정보와 지원 대상이 크게 충돌하지 않습니다.")
            filtered.append({"id": p.id, "reason": " ".join(why)[:180]})

    return filtered[:3]
