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

# 일학습병행 훈련과정
def parse_workstudy_policy(item):
    return {
        # 식별
        "source": "work",
        "source_id": item.get("훈련과정ID"),

        # 기본 정보
        "title": item.get("과정명"),
        "summary": item.get("자격증") or None,
        "detail_link": item.get("과정링크"),

        # 지역
        "region_sido": None,
        "region_sigungu": item.get("훈련기관주소"),
        "region_code": item.get("지역코드"),

        # 연령 (No data)
        "min_age": None,
        "max_age": None,

        # 조건 (구조 차이 핵심)
        "employment_requirements": to_list(
            item.get("훈련대상"),
            item.get("훈련대상코드"),
        ),
        "education_requirements": [],
        "major_requirements": to_list(item.get("NCS코드")),

        "income_requirements": [],
        "special_target": to_list(item.get("훈련대상")),

        # 기관
        "provider": item.get("훈련기관명"),
        "apply_method": "일학습병행",

        # 기간
        "start_date": parse_date(item.get("훈련시작일")),
        "end_date": parse_date(item.get("훈련종료일")),

        # 상태
        "status": "ACTIVE",

        # 원본
        "raw": item,
    }
