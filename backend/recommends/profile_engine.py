from typing import List

from django.contrib.auth.models import User

from collections import defaultdict
from typing import List

from django.contrib.auth.models import User

from policies.serializers import PolicyBasicSerializer
from .services.profile_candidates import get_profile_candidates

from .scoring.profile_score import calculate_profile_score, category_bucket, _map_profile_interest
from .reason.profile_reason import build_profile_reason
from .reason.profile_reason_ai import build_profile_reason_ai


def _profile_interest_buckets(profile) -> List[str]:
    """
    프로필의 관심 주제를 버킷으로 변환.
    """
    buckets: List[str] = []
    interest_categories = getattr(profile, "interest_categories", None)
    if interest_categories and isinstance(interest_categories, (list, tuple, set)):
        for item in interest_categories:
            mapped = _map_profile_interest(item)
            if mapped:
                buckets.append(mapped)
    else:
        mapped = _map_profile_interest(getattr(profile, "interest", None))
        if mapped:
            buckets.append(mapped)
    # 중복 제거
    seen = set()
    unique = []
    for b in buckets:
        if b in seen:
            continue
        seen.add(b)
        unique.append(b)
    return unique


def profile_recommend(user: User):
    """
    프로필 기반 추천: DB 하드 필터 -> 점수 계산 -> 정렬/슬라이싱.
    """
    profile = getattr(user, "profile", None)
    candidates = get_profile_candidates(profile)
    profile_targets = {str(t).strip().lower() for t in getattr(profile, "special_targets", []) if t}
    REQUIRED_TARGET_KEYWORDS = {"장애", "보훈", "저소득", "한부모", "군인"}
    GENDER_KEYS = {
        "female": {"여성", "여자", "female"},
        "male": {"남성", "남자", "male"},
    }
    profile_gender = (getattr(profile, "gender", None) or "").lower()

    scored = []
    for policy in candidates:
        policy_targets = {str(t).strip().lower() for t in getattr(policy, "special_target", []) if t}
        required_targets = {t for t in policy_targets if any(key in t for key in REQUIRED_TARGET_KEYWORDS)}
        # 필수 키워드(장애/보훈/저소득/한부모/군인)만 하드컷 유지, 그 외 타겟은 가산점에 맡김
        if required_targets and profile_targets and not (required_targets & profile_targets):
            continue
        if required_targets and not profile_targets:
            continue

        # 성별 지정 정책은 프로필 성별 불일치 또는 미지정 시 제외
        if policy_targets:
            lowered_targets = "".join(policy_targets)
            if any(k in lowered_targets for k in GENDER_KEYS["female"]):
                if not profile_gender or profile_gender not in GENDER_KEYS["female"]:
                    continue
            if any(k in lowered_targets for k in GENDER_KEYS["male"]):
                if not profile_gender or profile_gender not in GENDER_KEYS["male"]:
                    continue

        score, reasons = calculate_profile_score(policy, profile)
        scored.append((policy, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    # 관심 주제 버킷 파악
    preferred_buckets = _profile_interest_buckets(profile)
    single_bucket = preferred_buckets[0] if len(preferred_buckets) == 1 else None

    # 카테고리 다양성 유지: 동일 버킷 최대 2개(다수 관심), 단일 관심이면 해당 버킷만
    diversified = []
    bucket_count = defaultdict(int)
    for policy, score, reasons in scored:
        bucket = category_bucket(getattr(policy, "category", None))
        if single_bucket and bucket != single_bucket:
            continue
        limit = 2 if not single_bucket else 10
        if bucket_count[bucket] >= limit:
            continue
        bucket_count[bucket] += 1
        diversified.append((policy, score, reasons))
        if len(diversified) >= 10:
            break
    top = diversified

    results: List[dict] = []
    for policy, score, reasons in top:
        ai_reason = build_profile_reason_ai(policy, profile)
        results.append(
            {
                "policy": policy,
                "score": score,
                "reason": ai_reason or build_profile_reason(reasons),
            }
        )

    serializer = PolicyBasicSerializer([r["policy"] for r in results], many=True)
    serialized_map = {item["id"]: item for item in serializer.data}

    return [
        {
            "policy_id": r["policy"].id,
            "title": r["policy"].title,
            "category": r["policy"].category,
            "score": r["score"],
            "reason": r["reason"],
            "policy": serialized_map.get(r["policy"].id),
        }
        for r in results
    ]
