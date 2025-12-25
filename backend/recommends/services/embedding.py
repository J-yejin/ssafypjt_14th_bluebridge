import os
from typing import List

import requests
from django.conf import settings


def _get_gms_key() -> str:
    key = os.getenv("GMS_KEY", getattr(settings, "GMS_KEY", None))
    if not key:
        raise RuntimeError("GMS_KEY is not configured")
    return key


def embed_texts(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """
    GMS 프록시를 통해 OpenAI Embeddings 호출.
    """
    api_key = _get_gms_key()
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {"model": model, "input": texts}
    resp = requests.post(
        "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    embeddings = [item["embedding"] for item in data.get("data", [])]
    if len(embeddings) != len(texts):
        raise RuntimeError("embedding count mismatch")
    return embeddings
