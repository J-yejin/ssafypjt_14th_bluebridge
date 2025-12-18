import json
from django.core.management.base import BaseCommand
from policies.models import Policy

from policies.services.loader_youth import parse_youth_policy
from policies.services.loader_welfare import parse_welfare_policy
from policies.services.loader_training import parse_training_policy
from policies.services.loader_workstudy import parse_workstudy_policy
from policies.services.loader_employment import parse_employment_policy


# 각 JSON → Policy(payload dict)로 변환하는 loader들
LOADER_CONFIG = [
    {
        "name": "youth",
        "file": "data/youth.json",
        "parser": parse_youth_policy,
    },
    {
        "name": "welfare",
        "file": "data/welfare.json",
        "parser": parse_welfare_policy,
    },
    {
        "name": "training",
        "file": "data/training.json",
        "parser": parse_training_policy,
    },
    {
        "name": "workstudy",
        "file": "data/workstudy.json",
        "parser": parse_workstudy_policy,
    },
    {
        "name": "employment",
        "file": "data/employment.json",
        "parser": parse_employment_policy,
    },
]


class Command(BaseCommand):
    help = "Load policy JSON files into policies_policy table"

    def handle(self, *args, **options):
        total_created = 0
        total_updated = 0

        for cfg in LOADER_CONFIG:
            name = cfg["name"]
            file_path = cfg["file"]
            parser = cfg["parser"]

            self.stdout.write(f"\n▶ Loading policies: {name}")

            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)

            created = 0
            updated = 0

            for item in items:
                # loader가 Policy 모델 필드에 맞춘 payload(dict)를 반환
                payload = parser(item)

                _, is_created = Policy.objects.update_or_create(
                    source=payload["source"],          # policies 필드
                    source_id=payload["source_id"],    # policies 필드 (unique)
                    defaults=payload,                  # policies 필드들
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
