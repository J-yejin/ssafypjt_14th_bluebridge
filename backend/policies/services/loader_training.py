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

# 내일배움카드
def parse_training_policy(item):
    return {
        # 식별
        "source": "training",
        "source_id": item.get("훈련ID"),

        # 기본 정보
        "title": item.get("강좌명"),
        "summary": item.get("자격증") or None,
        "detail_link": item.get("상태링크"),

        # 지역
        "region_sido": None,
        "region_sigungu": item.get("주소"),
        "region_code": item.get("지역코드"),

        # 연령 (내일배움카드에는 없음)
        "min_age": None,
        "max_age": None,

        # 조건
        "employment_requirements": to_list(item.get("훈련대상"), item.get("훈련대상코드")),
        "education_requirements": [],
        "major_requirements": to_list(item.get("NCS코드")),

        "income_requirements": [],
        "special_target": [],

        # 기관
        "provider": item.get("교육원명"),
        "apply_method": "내일배움카드",

        # 기간
        "start_date": parse_date(item.get("훈련시작일")),
        "end_date": parse_date(item.get("훈련종료일")),

        # 상태
        "status": "ACTIVE",

        # 원본
        "raw": item,
    }
