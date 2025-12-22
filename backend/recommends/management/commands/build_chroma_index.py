import chromadb
from django.core.management.base import BaseCommand

from recommends.engine import (
    CHROMA_DIR,
    COLLECTION_NAME,
    build_embedding_text,
    embed_texts,
)
from policies.models import Policy


def _meta_value(val):
    """
    Chroma 메타데이터는 str/int/float/bool만 허용.
    리스트는 콤마로 이어 붙여 문자열로 저장한다.
    """
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, list):
        return ",".join([str(v) for v in val])
    return str(val)


class Command(BaseCommand):
    help = "정책 데이터를 Chroma 컬렉션에 임베딩/업서트합니다."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=64)
        parser.add_argument("--reset", action="store_true", help="기존 컬렉션 삭제 후 재생성")

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

        qs = Policy.objects.filter(status="ACTIVE").order_by("id")
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("업서트할 정책이 없습니다."))
            return

        self.stdout.write(f"총 {total}개 정책 업서트 시작 (batch={batch_size})")
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
                ids.append(str(p.id))
                docs.append(text)
                metadatas.append(
                    {
                        "policy_type": _meta_value(p.policy_type),
                        "region_scope": _meta_value(p.region_scope),
                        "region_sido": _meta_value(p.region_sido),
                        "min_age": _meta_value(p.min_age),
                        "max_age": _meta_value(p.max_age),
                        "employment": _meta_value(p.employment),
                        "education": _meta_value(p.education),
                        "major": _meta_value(p.major),
                        "special_target": _meta_value(p.special_target),
                    }
                )

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

        self.stdout.write(self.style.SUCCESS("Chroma 업서트 완료"))
