# policies/management/commands/load_policies.py

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from policies.models import Policy

from policies.services.loader_youth import parse_youth_policy
from policies.services.loader_welfare_central import parse_welfare_central_policy
from policies.services.loader_welfare_local import parse_welfare_local_policy


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# JSON -> Policy 매핑 설정
LOADER_CONFIG = [
    {
        "name": "youth_policy",
        "file": BASE_DIR / "data/youth_policy.json",
        "parser": parse_youth_policy,
    },
    {
        "name": "welfare_central",
        "file": BASE_DIR / "data/welfare_central.json",
        "parser": parse_welfare_central_policy,
    },
    {
        "name": "welfare_local",
        "file": BASE_DIR / "data/welfare_local.json",
        "parser": parse_welfare_local_policy,
    },
]


class Command(BaseCommand):
    help = "Load youth / welfare policy JSON files into Policy table"

    def handle(self, *args, **options):
        total_created = 0
        total_updated = 0

        for cfg in LOADER_CONFIG:
            name = cfg["name"]
            file_path = cfg["file"]
            parser = cfg["parser"]

            self.stdout.write(f"\n▶ Loading policies: {name}")

            if not file_path.exists():
                self.stdout.write(
                    self.style.WARNING(f"  - File not found: {file_path}")
                )
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)

            created = 0
            updated = 0

            for item in items:
                payload = parser(item)

                _, is_created = Policy.objects.update_or_create(
                    source=payload["source"],
                    source_id=payload["source_id"],
                    defaults=payload,
                )

                if is_created:
                    created += 1
                else:
                    updated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  - {name}: created={created}, updated={updated}"
                )
            )

            total_created += created
            total_updated += updated

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ DONE | total created={total_created}, total updated={total_updated}"
            )
        )
