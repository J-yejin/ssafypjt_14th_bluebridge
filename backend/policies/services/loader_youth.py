import json
from datetime import datetime
from pathlib import Path


# =========================
# 공통 유틸
# =========================
def parse_date(value):
    if not value or not str(value).strip():
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def split_codes(value):
    """
    "001,002,003" → ["001", "002", "003"]
    """
    if not value or not isinstance(value, str):
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def map_codes_to_text(codes, mapping_dict):
    """
    ["001", "002"] → ["재직자", "미취업자"]
    매핑 실패 시 원본 코드 유지
    """
    return [mapping_dict.get(code, code) for code in codes]


# =========================
# 매핑 파일 로드
# =========================
BASE_DIR = Path(__file__).resolve().parents[2] / "data"

with open(BASE_DIR / "region_code_mapping.json", encoding="utf-8") as f:
    REGION_CODE_MAP = json.load(f)

with open(BASE_DIR / "user_condition_code_mapping.json", encoding="utf-8") as f:
    CONDITION_CODE_MAP = json.load(f)


# =========================
# 코드 → 텍스트 매핑
# =========================
def map_condition_codes(value, category):
    codes = split_codes(value)
    mapping = CONDITION_CODE_MAP.get(category, {})
    return map_codes_to_text(codes, mapping)


def map_region_codes(value):
    codes = split_codes(value)
    return map_codes_to_text(codes, REGION_CODE_MAP)

# =========================
# search_summary 생성 함수
# =========================
def build_search_summary(*values):
    tokens = []
    for value in values:
        if isinstance(value, list):
            tokens.extend(value)
        elif isinstance(value, str):
            tokens.append(value)

    # 중복 제거 + 정제
    tokens = list(dict.fromkeys([t.strip() for t in tokens if t and t.strip()]))

    summary = " ".join(tokens)
    return summary


# =========================
# Youth Policy Parser
# =========================
def parse_youth_policy(item):
    # -------------------------
    # 지역 처리
    # -------------------------
    applicable_regions = map_region_codes(item.get("정책거주지역코드"))

    if not applicable_regions:
        region_scope = "NATIONWIDE"
        region_sido = None
    elif len(applicable_regions) == 1:
        region_scope = "LOCAL"
        region_sido = applicable_regions[0]
    else:
        region_scope = "LOCAL"
        region_sido = "복수지역"

    # -------------------------
    # 조건 매핑
    # -------------------------
    employment = map_condition_codes(
        item.get("정책취업요건코드"), "취업요건"
    )

    education = map_condition_codes(
        item.get("정책학력요건코드"), "학력요건"
    )

    major = map_condition_codes(
        item.get("정책전공요건코드"), "전공요건"
    )

    # -------------------------
    # 정책 제공방법 → benefit_type
    # -------------------------
    benefit_type = map_condition_codes(
        item.get("정책제공방법코드"), "정책제공방법"
    )
    
    special_target = map_condition_codes(
        item.get("정책특화요건코드"), "특화요건"
    )
    # benefit_type = benefit_types[0] if benefit_types else None

    # -------------------------
    # 검색용 summary 생성
    # -------------------------
    search_summary = build_search_summary(
    item.get("정책명"),
    split_codes(item.get("정책키워드명")),
    employment,
    special_target,
    benefit_type,
)
    
    return {
        # =====================
        # 1. 식별 / 출처
        # =====================
        "source": "youth",
        "source_id": item.get("정책번호"),
        "policy_type": "YOUTH",

        # =====================
        # 2. 기본 정보
        # =====================
        "title": item.get("정책명"),
        "summary": item.get("정책설명내용"),
        "search_summary": search_summary,
        "keywords": split_codes(item.get("정책키워드명")),

        # =====================
        # 3. 카테고리
        # =====================
        "category": item.get("정책대분류명"),

        # =====================
        # 4. 지역
        # =====================
        "region_scope": region_scope,
        "region_sido": region_sido,
        "region_sigungu": None,
        "applicable_regions": applicable_regions,

        # =====================
        # 5. 연령
        # =====================
        "min_age": int(item["지원대상최소연령"]) if item.get("지원대상최소연령") else None,
        "max_age": int(item["지원대상최대연령"]) if item.get("지원대상최대연령") else None,

        # =====================
        # 6. 취업 상태
        # =====================
        "employment": employment,

        # =====================
        # 7. 조건 정보
        # =====================
        "education": education,
        "major": major,
        "special_target": special_target,
        "target_detail": item.get("추가신청자격조건내용") +"/" + item.get("참여제외대상내용"),

        # =====================
        # 8. 운영 / 지원 정보
        # =====================
        "provider": item.get("주관기관코드명"),
        "apply_method": None,
        "detail_links": item.get("참고URL주소1"),
        "detail_contact" : [],
            
        "service_type": benefit_type,
        "policy_detail": item.get("정책지원내용"),

        # =====================
        # 9. 신청 가능 여부
        # =====================
        "start_date": parse_date(item.get("사업시작일")),
        "end_date": parse_date(item.get("사업종료일")),

        # =====================
        # 10. 상태 / 원본
        # =====================
        "status": "ACTIVE",
        "raw": item,
    }
