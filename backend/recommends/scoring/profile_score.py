from typing import List, Optional, Tuple

# 데이터 카테고리 -> 프론트/버킷 매핑
DATA_CATEGORY_MAP = {
    "일자리": "일자리",
    "취업": "일자리",
    "창업": "창업",
    "교육": "교육",
    "문화·여가": "복지문화",
    "복지문화": "복지문화",
    "신체건강": "건강",
    "정신건강": "건강",
    "생활지원": "생활지원",
    "보육": "생활지원",
    "보호·돌봄": "생활지원",
    "주거": "생활지원",
    "서민금융": "재무/법률",
    "법률": "재무/법률",
    "안전·위기": "위기·안전",
    "임신·출산": "가족/권리",
    "입양·위탁": "가족/권리",
    "참여권리": "가족/권리",
}

# 프로필 관심(취업/교육/주거/문화/건강/지역/창업 등) -> 데이터 카테고리 버킷 매핑
PROFILE_INTEREST_MAP = {
    "취업": "일자리",
    "일자리": "일자리",
    "교육": "교육",
    "문화": "복지문화",
    "복지문화": "복지문화",
    "건강": "건강",
    "주거": "생활지원",
    "생활지원": "생활지원",
    "재무": "재무/법률",
    "법률": "재무/법률",
    "위기": "위기·안전",
    "안전": "위기·안전",
    "지역": "가족/권리",
    "창업": "창업",
}


def _map_policy_category(category: Optional[str]) -> Optional[str]:
    if not category:
        return None
    return DATA_CATEGORY_MAP.get(category.strip())


def _map_profile_interest(profile_interest: Optional[str]) -> Optional[str]:
    if not profile_interest:
        return None
    return PROFILE_INTEREST_MAP.get(profile_interest.strip())


def _interest_bucket_match(policy_category: Optional[str], profile_interest: Optional[str]) -> bool:
    if not policy_category or not profile_interest:
        return False
    return _map_policy_category(policy_category) == _map_profile_interest(profile_interest)


def category_bucket(category: Optional[str]) -> str:
    """
    공개용 카테고리 버킷 매퍼. 매칭되지 않으면 원본 또는 '기타'.
    """
    mapped = _map_policy_category(category)
    if mapped:
        return mapped
    if category:
        return category.strip()
    return "기타"


def calculate_profile_score(policy, profile) -> Tuple[float, List[str]]:
    """
    가중치 기반 점수 계산 + 이유 목록 반환.
    """
    score = 0.0
    reasons: List[str] = []

    # 관심 정보: interest_categories (list) 우선, 없으면 interest 단일 값
    interest_categories = getattr(profile, "interest_categories", None)
    profile_interest_value = None
    if interest_categories and isinstance(interest_categories, (list, tuple, set)):
        profile_interest_value = next((x for x in interest_categories if x), None)
    else:
        profile_interest_value = getattr(profile, "interest", None)
    profile_region = getattr(profile, "region_sido", None) or getattr(profile, "region", None)

    # 관심 카테고리 (패턴 A) - 매핑 후 비교
    if _interest_bucket_match(policy.category, profile_interest_value):
        score += 0.5
        reasons.append("관심 주제와 일치하는 정책입니다.")

    # 지역 (패턴 B/C): 지역 일치에 더 높은 가중치, 전국은 보조 가중치
    if policy.region_scope == "NATIONWIDE":
        score += 0.25
        reasons.append("거주 지역과 관계없이 신청할 수 있는 전국 대상 정책입니다.")
    elif profile_region and policy.region_sido == profile_region:
        score += 0.45
        reasons.append(f"{profile_region} 거주자를 대상으로 한 정책입니다.")

    # 정책 유형 (패턴 D)
    if getattr(policy, "policy_type", None) == "YOUTH":
        score += 0.15
        reasons.append("청년을 대상으로 한 정책입니다.")

    # 스페셜 타겟 매칭 시 가산
    profile_targets = {str(t).strip().lower() for t in getattr(profile, "special_targets", []) if t}
    policy_targets = {str(t).strip().lower() for t in getattr(policy, "special_target", []) if t}
    if profile_targets and policy_targets and (profile_targets & policy_targets):
        score += 0.2
        reasons.append("프로필의 특수 대상과 일치합니다.")

    return score, reasons
