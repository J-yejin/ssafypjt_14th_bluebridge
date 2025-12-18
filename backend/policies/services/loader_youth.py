from datetime import datetime

# 공통 함수
# 날짜 처리, list화
def parse_date(value):
    if not value or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except:
        try:
            return datetime.strptime(value.strip(), "%Y%m%d").date()
        except:
            return None

def to_list(*values):
    return [v for v in values if v]

# 청년정보통 청년 정책
def parse_youth_policy(item):
    return {
        # 식별
        "source": "youth",
        "source_id": item.get("정책번호"),

        # 기본 정보
        "title": item.get("정책명"),
        "summary": item.get("정책설명"),
        "detail_link": item.get("신청URL"),

        # 지역
        "region_sido": item.get("지역분류"),
        "region_sigungu": None,
        "region_code": item.get("지역코드"),

        # 연령
        "min_age": int(item["최소연령"]) if item.get("최소연령") else None,
        "max_age": int(item["최대연령"]) if item.get("최대연령") else None,

        # 조건
        "employment_requirements": to_list(item.get("취업요건")),
        "education_requirements": to_list(item.get("학력요건")),
        "major_requirements": to_list(item.get("전공요건")),
        "income_requirements": [
            item.get("최소소득"),
            item.get("최대소득"),
        ] if item.get("최소소득") or item.get("최대소득") else [],

        "special_target": [],

        # 기관
        "provider": item.get("주관기관명"),
        "apply_method": None,

        # 기간
        "start_date": parse_date(item.get("사업시작일")),
        "end_date": parse_date(item.get("사업종료일")),

        # 상태
        "status": "ACTIVE",

        # 원본 보존
        "raw": item,
    }

