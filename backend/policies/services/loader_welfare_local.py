# loader_welfare_local.py

from datetime import datetime


# =========================
# 공통 유틸
# =========================
def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except Exception:
        return None


def split_text(value, sep=","):
    """
    "방문, 인터넷" → ["방문", "인터넷"]
    """
    if not value or not isinstance(value, str):
        return []
    return [v.strip() for v in value.split(sep) if v.strip()]

# ==========================
# special_target 처리 유틸
# ==========================
def build_special_target(item):
    """
    지원대상 + 지원대상내용 → special_target 리스트
    """
    target = item.get("지원대상")
    detail = item.get("지원대상내용")

    if not target and not detail:
        return []

    return [{
        "title": target,
        "description": detail,
    }]

# =========================
# Welfare Local Parser
# =========================
def parse_welfare_local_policy(item):
    # -------------------------
    # 지역 처리
    # -------------------------
    region_sido = item.get("시도")
    region_sigungu = item.get("시군구")

    if region_sido:
        region_scope = "LOCAL"
        applicable_regions = [region_sido]
    else:
        region_scope = "NATIONWIDE"
        applicable_regions = []

    # -------------------------
    # 키워드 구성
    # -------------------------
    keywords = (
        split_text(item.get("관심주제")) +
        split_text(item.get("생애주기")) +
        ([item.get("지원대상")] if item.get("지원대상") else [])
    )

    # -------------------------
    # 신청 방법
    # -------------------------
    apply_method = ", ".join(split_text(item.get("신청방법")))

    return {
        # =====================
        # 1. 식별 / 출처
        # =====================
        "source": "welfare_local",
        "source_id": item.get("서비스ID"),
        "policy_type": "WELFARE",

        # =====================
        # 2. 기본 정보
        # =====================
        "title": item.get("서비스명"),
        "summary": item.get("서비스요약"),
        "search_summary": item.get("서비스요약"),
        "keywords": keywords,

        # =====================
        # 3. 카테고리
        # =====================
        "category": item.get("관심주제"),

        # =====================
        # 4. 지역
        # =====================
        "region_scope": region_scope,
        "region_sido": region_sido,
        "region_sigungu": region_sigungu if region_sigungu != "-" else None,
        "applicable_regions": applicable_regions,

        # =====================
        # 5. 연령
        # =====================
        "min_age": None,
        "max_age": None,

        # =====================
        # 6. 취업 상태
        # =====================
        "employment_status": [],

        # =====================
        # 7. 조건 정보
        # =====================
        "education": [],
        "major": [],
        "special_target": build_special_target(item),

        # =====================
        # 8. 운영 / 지원 정보
        # =====================
        "provider": item.get("담당부서"),
        "apply_method": item.get("지원주기") + "주기로" + apply_method,
        "apply_links": item.get("상세링크") or item.get("관련사이트"),

        "benefit_type": item.get("서비스유형"),
        "benefit_detail": item.get("지원내용"),

        # =====================
        # 9. 신청 가능 여부
        # =====================
        "start_date": parse_date(item.get("시행시작일")),
        "end_date": parse_date(item.get("시행종료일")),

        # =====================
        # 10. 상태 / 원본
        # =====================
        "status": "ACTIVE",
        "raw": item,
    }
