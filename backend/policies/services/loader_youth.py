import json
from datetime import datetime
from pathlib import Path


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

# mapping 파일 로드
BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "region_code_mapping.json", encoding="utf-8") as f:
    REGION_CODE_MAP = json.load(f)

with open(BASE_DIR / "user_condition_code_mapping.json", encoding="utf-8") as f:
    CONDITION_CODE_MAP = json.load(f)


# 코드 문자열을 코드 리스트로 변환
def split_codes(value):
    """
    "001,002,003" → ["001", "002", "003"]
    """
    if not value or not isinstance(value, str):
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

    
# 텍스트 매핑 함수
def map_codes_to_text(codes, mapping_dict):
    """
    ["001", "002"] → ["재직자", "미취업자"]
    매핑 실패 시 원본 코드 유지
    """
    results = []
    for code in codes:
        results.append(mapping_dict.get(code, code))
    return results


# 조건 코드 매핑 함수
def map_condition_codes(value, category):
    """
    콤마로 구분된 코드 문자열 → 텍스트 리스트
    """
    codes = split_codes(value)
    mapping = CONDITION_CODE_MAP.get(category, {})
    return map_codes_to_text(codes, mapping)

# 지역 코드 매핑 함수
def map_region_codes(value):
    codes = split_codes(value)
    return map_codes_to_text(codes, REGION_CODE_MAP)


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

        # 지역 (다중 코드 → 텍스트)
        "region_sido": item.get("지역분류"),
        "region_sigungu": map_region_codes(item.get("지역코드")),

        # 연령
        "min_age": int(item["최소연령"]) if item.get("최소연령") else None,
        "max_age": int(item["최대연령"]) if item.get("최대연령") else None,

        # 조건 (다중 코드 처리)
        "employment_requirements": map_condition_codes(
            item.get("취업요건"), "취업요건"
        ),

        "education_requirements": map_condition_codes(
            item.get("학력요건"), "학력요건"
        ),

        "major_requirements": map_condition_codes(
            item.get("전공요건"), "전공요건"
        ),

        "income_requirements": [
            v for v in [
                item.get("최소소득"),
                item.get("최대소득"),
            ] if v
        ],

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
