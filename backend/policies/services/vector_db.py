from pathlib import Path
from typing import Dict, List, Optional, Sequence

import chromadb
from chromadb.api import ClientAPI, Collection
from chromadb.config import Settings

# Chroma 저장 위치를 recommends 앱 내부에 고정
CHROMA_DIR = Path(__file__).resolve().parents[2] / "recommends" / "chroma_index"
COLLECTION_NAME = "policies"


def _client() -> ClientAPI:
    """
    PersistentClient를 반환. 텔레메트리는 비활성화해 불필요한 네트워크를 막는다.
    """
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(name: str = COLLECTION_NAME) -> Collection:
    """
    컬렉션을 가져오되 없으면 생성. 메타데이터 스페이스는 cosine 고정.
    """
    client = _client()
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name, metadata={"hnsw:space": "cosine"})


def upsert(
    ids: Sequence[str],
    embeddings: Sequence[Sequence[float]],
    metadatas: Sequence[Dict],
    documents: Sequence[str],
    name: str = COLLECTION_NAME,
) -> None:
    """
    벡터/문서를 업서트. ids와 embeddings 길이가 일치해야 한다.
    """
    collection = get_or_create_collection(name)
    collection.upsert(
        ids=list(ids),
        embeddings=list(embeddings),
        metadatas=list(metadatas),
        documents=list(documents),
    )


def query(
    query_embeddings: Sequence[Sequence[float]],
    where: Optional[Dict] = None,
    top_k: int = 10,
    name: str = COLLECTION_NAME,
) -> Dict:
    """
    컬렉션 쿼리 헬퍼.
    """
    collection = get_or_create_collection(name)
    return collection.query(
        query_embeddings=list(query_embeddings),
        n_results=top_k,
        where=where,
    )
