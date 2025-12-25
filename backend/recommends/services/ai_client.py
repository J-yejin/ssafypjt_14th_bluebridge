import os
from pathlib import Path
from typing import Any, Dict, List

import requests
from django.conf import settings


def _load_env():
    """
    Minimal .env loader (no external deps). Looks for .env at project root (backend와 같은 레벨).
    """
    try:
        env_path = Path(__file__).resolve().parents[3] / ".env"
        if not env_path.exists():
            return
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        return


def _get_gms_key() -> str:
    key = os.getenv("GMS_KEY", getattr(settings, "GMS_KEY", None))
    if not key:
        _load_env()
        key = os.getenv("GMS_KEY", getattr(settings, "GMS_KEY", None))
    if not key:
        raise RuntimeError("GMS_KEY is not configured")
    return key


def chat_completion(messages: List[Dict[str, Any]], model: str = "gpt-4o-mini") -> str:
    """
    GMS 프록시를 통해 OpenAI Chat Completions 호출.
    """
    api_key = _get_gms_key()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": messages,
    }
    resp = requests.post(
        "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
