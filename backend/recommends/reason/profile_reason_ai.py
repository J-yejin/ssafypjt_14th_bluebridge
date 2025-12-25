from typing import Optional

from ..services.ai_client import chat_completion


def build_profile_reason_ai(policy, profile) -> str:
    """
    LLM으로 프로필 기반 추천 이유 생성. 실패 시 빈 문자열 반환.
    """
    policy_summary = getattr(policy, "summary", "") or getattr(policy, "search_summary", "") or ""
    policy_region = getattr(policy, "region_scope", "") or ""
    profile_region = getattr(profile, "region_sido", None) or getattr(profile, "region", None) or ""
    profile_interest = getattr(profile, "interest", None) or ""

    system = (
        "너는 정책 추천 카드의 설명을 짧게 써주는 보조야. 한국어로 한 문장(50자 내외)으로 답해."
        "알고리즘 설명 없이, 사용자 관심/지역과 정책 내용을 연결해서 설명해."
    )
    user = (
        f"정책 제목: {getattr(policy, 'title', '')}\n"
        f"정책 요약: {policy_summary}\n"
        f"정책 지역: {policy_region}\n"
        f"사용자 관심: {profile_interest}\n"
        f"사용자 지역: {profile_region}\n"
        "한 문장으로, 친근하게 작성해."
    )
    try:
        text = chat_completion(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            model="gpt-4o-mini",
        ).strip()
        return text[:80]
    except Exception:
        return ""
