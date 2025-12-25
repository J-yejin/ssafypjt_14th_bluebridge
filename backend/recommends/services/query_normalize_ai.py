import json
from typing import Dict, Optional

from .ai_client import chat_completion


def normalize_query_llm(query: str) -> Dict[str, Optional[str]]:
    """
    LLM을 사용해 질의를 요약/정규화.
    """
    system = (
        "너는 한국어 정책 검색 보조야. 사용자의 질의를 간결한 의도 문장으로 정리하고, "
        "핵심 키워드만 쉼표로 분리해 반환해. JSON으로만 답변해."
    )
    user = (
        f"입력 질의: {query}\n"
        "아래 JSON 포맷으로만 출력:\n"
        '{ "intent": "<짧은 의도 문장>", "keywords": ["키워드1","키워드2"] }\n'
        "불확실하면 intent는 입력 그대로, keywords는 비워도 된다."
    )
    try:
        raw = chat_completion(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            model="gpt-4o-mini",
        )
        data = json.loads(raw)
        intent = data.get("intent") or query
        keywords = data.get("keywords") or []
        return {"intent": intent, "keywords": keywords}
    except Exception:
        return {"intent": query, "keywords": []}
