from datetime import datetime

def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except:
        return None

def to_list(*values):
    return [v for v in values if v]

# 구직자 취업역량
def parse_employment_policy(item):
    source_id = f"{item.get('고용센터명')}_{item.get('과정명')}"

    return {
        # 식별
        "source": "employment",
        "source_id": source_id,

        # 기본 정보
        "title": item.get("과정명"),
        "summary": item.get("프로그램명"),
        "detail_link": None,

        # 지역
        "region_sido": None,
        "region_sigungu": item.get("장소"),
        "region_code": None,

        # 연령 (문자열 대상자에서만 암시됨)
        "min_age": None,
        "max_age": None,

        # 조건
        "employment_requirements": to_list(item.get("대상자")),
        "education_requirements": [],
        "major_requirements": [],
        "income_requirements": [],
        "special_target": [],

        # 기관
        "provider": item.get("고용센터명"),
        "apply_method": "고용센터 프로그램",

        # 기간
        "start_date": parse_date(item.get("과정시작일")),
        "end_date": parse_date(item.get("과정종료일")),

        # 상태
        "status": "ACTIVE",

        # 원본
        "raw": item,
    }
