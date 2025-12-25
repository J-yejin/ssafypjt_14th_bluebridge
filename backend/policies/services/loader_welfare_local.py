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

# =========================
# 문의처, 관련 링크 -> 리스트 변환
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
                "contact": url,
            })
    return results

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
    # 카테고리
    # -------------------------
    category = item.get("관심주제")
    
    # -------------------------
    # 키워드 구성
    # -------------------------
    keywords = []
    if category:
        keywords.append(category)
    keywords.extend(split_text(item.get("생애주기")))
    
    detail_links = []
    detail_links.extend({"복지로 사이트": item.get("상세링크")})
    detail_links.extend(build_apply_links(item.get("관련사이트")))


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
        "category": category,

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
        "employment": [],

        # =====================
        # 7. 조건 정보
        # =====================
        "education": [],
        "major": [],
        "special_target": item.get("지원대상"),
        "target_detail": [item.get("지원대상내용"), item.get("선정기준")],

        # =====================
        # 8. 운영 / 지원 정보
        # =====================
        "provider": item.get("담당부서"),
        "apply_method": item.get("지원주기") + "주기로" + item.get("신청방법상세"),
        "detail_links": detail_links,
        "detail_contact": build_apply_links(item.get("문의처")),

        "service_type": item.get("서비스유형"),
        "policy_detail": item.get("지원내용"),

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
