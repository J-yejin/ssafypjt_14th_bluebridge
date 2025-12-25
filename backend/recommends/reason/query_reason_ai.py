from typing import Optional

from ..services.ai_client import chat_completion


def build_query_reason_ai(policy, query: str, summary: Optional[str] = None) -> str:
    """
    LLM으로 질의-정책 연결 이유를 생성. 실패 시 빈 문자열 반환.
    """
    if isinstance(policy, dict):
        title = policy.get("title", "")
        summary_text = summary or policy.get("summary") or policy.get("search_summary") or ""
    else:
        title = getattr(policy, "title", "")
        summary_text = summary or getattr(policy, "summary", "") or getattr(policy, "search_summary", "") or ""

    system = (
        "너는 정책 추천 이유를 짧게 생성하는 보조야. 한국어로 한 문장(50~80자)으로 답해. "
        "알고리즘 설명 없이, 사용자의 질의와 정책 내용을 연결해서 구체적으로 설명해. "
        "가능하면 지역/혜택/대상 단어를 포함해줘."
    )
    user = (
        f"사용자 질의: {query}\n"
        f"정책 제목: {title}\n"
        f"정책 요약: {summary_text}\n"
        "한 문장으로, 50자 내외로 작성해."
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
