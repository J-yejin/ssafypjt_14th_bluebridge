# loader_welfare_central.py

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
    "청년, 중장년" → ["청년", "중장년"]
    """
    if not value or not isinstance(value, str):
        return []
    return [v.strip() for v in value.split(sep) if v.strip()]


# =========================
# 텍스트 -> 리스트 변환
# =========================
def build_apply_links(site_list):
    """
    사이트목록 → [{name, url}, ...]
    """
    if not site_list or not isinstance(site_list, list):
        return []

    results = []
    for site in site_list:
        url = site.get("상세정보")
        name = site.get("상세명")
        if url:
            results.append({
                "name": name,
                "url": url,
            })
    return results


# =========================
# Welfare Central Parser
# =========================
def parse_welfare_central_policy(item):
    """
    복지로 중앙부처 서비스 → Policy 모델 매핑
    """
    # 중앙부처 복지는 전국 단위
    region_scope = "NATIONWIDE"

    # 카테고리: 관심주제 기준 (일자리 / 생활지원 등)
    category = item.get("관심주제")

    # 키워드 구성
    keywords = []
    if category:
        keywords.append(category)
    keywords.extend(split_text(item.get("생애주기")))

    # 혜택 유형
    benefit_type = item.get("제공유형")

    # 혜택 상세
    benefit_detail = item.get("급여서비스내용")

    return {
        # =====================
        # 1. 식별 / 출처
        # =====================
        "source": "welfare_central",
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
        "category": category,

        # =====================
        # 4. 지역
        # =====================
        "region_scope": region_scope,
        "region_sido": None,
        "region_sigungu": None,
        "applicable_regions": [],

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
        "special_target": [item.get("가구유형")] if item.get("가구유형") else [],

        # =====================
        # 8. 운영 / 지원 정보
        # =====================
        "provider": item.get("소관부처명"),
        "apply_method": item.get("지원주기")+"(으)로 신청",
        "apply_links": build_apply_links(item.get("사이트목록")),

        "benefit_type": benefit_type,
        "benefit_detail": benefit_detail,

        # =====================
        # 9. 신청 가능 여부
        # =====================
        "start_date": parse_date(item.get("기준연도")),
        "end_date": parse_date(item.get("기준연도")),

        # =====================
        # 10. 상태 / 원본
        # =====================
        "status": "ACTIVE",
        "raw": item,
    }
