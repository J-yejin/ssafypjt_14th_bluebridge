import json
from pathlib import Path

from django.core.management.base import BaseCommand

from policies.models import Policy


class Command(BaseCommand):
    help = "ACTIVE 정책을 JSON 인덱스로 덤프"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, default="backend/recommends/data/policy_index.json")

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        qs = Policy.objects.filter(status="ACTIVE").order_by("id")
        items = []
        for p in qs:
            items.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "search_summary": p.search_summary or "",
                    "summary": p.summary or "",
                    "category": p.category or "",
                    "region_scope": p.region_scope or "",
                    "region_sido": p.region_sido or "",
                    "applicable_regions": p.applicable_regions or [],
                    "min_age": p.min_age,
                    "max_age": p.max_age,
                }
            )

        output_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Dumped {len(items)} policies to {output_path}"))
