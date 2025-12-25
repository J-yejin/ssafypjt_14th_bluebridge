import json
from pathlib import Path
from typing import List, Dict

INDEX_PATH = Path("backend/recommends/data/policy_index.json")

_CACHE: List[Dict] = []


def load_index() -> List[Dict]:
    global _CACHE
    if _CACHE:
        return _CACHE
    if not INDEX_PATH.exists():
        return []
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    _CACHE = data
    return data
