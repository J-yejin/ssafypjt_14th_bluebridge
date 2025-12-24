import hashlib

import chromadb
from typing import List
from django.core.management.base import BaseCommand

from recommends.engine import (
    CHROMA_DIR,
    COLLECTION_NAME,
    build_embedding_text,
    embed_texts,
)
from policies.models import Policy


def _normalize_meta_value(val):
    """
    Normalize metadata for Chroma:
    - None -> None
    - list/tuple/set -> lowercased, trimmed strings joined with "|"
      (Chroma metadata must be scalar)
    - scalar -> lowercased string
    """
    if val is None:
        return None
    if isinstance(val, (list, tuple, set)):
        normalized_list: List[str] = []
        for v in val:
            if v is None:
                continue
            normalized_list.append(str(v).strip().lower())
        return "|".join([v for v in normalized_list if v])
    return str(val).strip().lower()


class Command(BaseCommand):
    help = "Build Chroma index for active policies."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=64)
        parser.add_argument("--reset", action="store_true", help="Drop existing collection before rebuild")

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

        # Load existing hashes to skip unchanged docs
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
            self.stdout.write(self.style.WARNING("No policies to embed."))
            return

        self.stdout.write(f"{total} policies embedding (batch={batch_size})")
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

                # Skip if content unchanged
                if existing_hash.get(pid_str) == content_hash:
                    continue

                ids.append(pid_str)
                docs.append(text)

                meta_raw = {
                    "policy_type": _normalize_meta_value(p.policy_type),
                    "category": _normalize_meta_value(p.category),
                    "region_scope": _normalize_meta_value(p.region_scope),
                    "region_sido": _normalize_meta_value(p.region_sido),
                    "applicable_regions": _normalize_meta_value(getattr(p, "applicable_regions", None)),
                    "min_age": p.min_age,
                    "max_age": p.max_age,
                    "employment": _normalize_meta_value(p.employment),
                    "education": _normalize_meta_value(p.education),
                    "major": _normalize_meta_value(p.major),
                    "special_target": _normalize_meta_value(p.special_target),
                    "keywords": _normalize_meta_value(getattr(p, "keywords", None)),
                    "service_type": _normalize_meta_value(getattr(p, "service_type", None)),
                    # change detection
                    "content_hash": content_hash,
                }

                cleaned_meta = {}
                for k, v in meta_raw.items():
                    if v is None:
                        continue
                    if isinstance(v, list) and not v:
                        continue
                    cleaned_meta[k] = v

                metadatas.append(cleaned_meta)

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
            self.stdout.write(f"- progress: {processed}/{total}")

        self.stdout.write(self.style.SUCCESS("Chroma index build done"))
