import chromadb
from django.core.management.base import BaseCommand
import hashlib

from recommends.engine import (
    CHROMA_DIR,
    COLLECTION_NAME,
    build_embedding_text,
    embed_texts,
)
from policies.models import Policy


def _meta_value(val):
    """
    메타데이터를 쿼리 친화적으로 가공.
    리스트는 원소를 문자열 리스트로 유지해 $contains 필터와 호환되도록 한다.
    """
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, list):
        return ",".join([str(v) for v in val])
    return str(val)


class Command(BaseCommand):
    help = "활성 정책을 Chroma 컬렉션에 임베딩/업서트합니다."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=64)
        parser.add_argument("--reset", action="store_true", help="기존 컬렉션 삭제 후 생성")

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        reset = options["reset"]

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        if reset:
            try:
                client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass

        try:
            collection = client.get_collection(COLLECTION_NAME)
        except Exception:
            collection = client.create_collection(
                COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
            )

        # 기존 메타데이터의 content_hash를 가져와 변경 여부 판단
        existing_hash = {}
        try:
            existing = collection.get(include=["metadatas", "ids"])
            for pid, meta in zip(existing.get("ids", []), existing.get("metadatas", [])):
                if meta and "content_hash" in meta:
                    existing_hash[str(pid)] = meta["content_hash"]
        except Exception:
            existing_hash = {}

        qs = Policy.objects.filter(status="ACTIVE").order_by("id")
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("임베딩할 정책이 없습니다."))
            return

        self.stdout.write(f"{total}개 정책 임베딩 시작 (batch={batch_size})")
        processed = 0
        for start in range(0, total, batch_size):
            batch = list(qs[start : start + batch_size])
            ids = []
            docs = []
            metadatas = []
            for p in batch:
                text = build_embedding_text(p)
                if not text:
                    continue
                pid_str = str(p.id)
                content_hash = hashlib.md5(text.encode("utf-8")).hexdigest()

                # 기존과 동일한 콘텐츠면 스킵
                if existing_hash.get(pid_str) == content_hash:
                    continue

                ids.append(pid_str)
                docs.append(text)
                meta_raw = {
                    "policy_type": _meta_value(p.policy_type),
                    "region_scope": _meta_value(p.region_scope),
                    "region_sido": _meta_value(p.region_sido),
                    "min_age": _meta_value(p.min_age),
                    "max_age": _meta_value(p.max_age),
                    "employment": _meta_value(p.employment),
                    "education": _meta_value(p.education),
                    "major": _meta_value(p.major),
                    "special_target": _meta_value(p.special_target),
                    "content_hash": content_hash,
                }
                # Chroma는 None을 허용하지 않으므로 제외
                metadatas.append({k: v for k, v in meta_raw.items() if v is not None})

            if not ids:
                continue

            embeddings = embed_texts(docs)
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=docs,
            )
            processed += len(ids)
            self.stdout.write(f"- 진행: {processed}/{total}")

        self.stdout.write(self.style.SUCCESS("Chroma 인덱스 구축 완료"))
