from django.db.models import Q

from policies.models import Policy


def get_profile_candidates(profile):
    """
    프로필 기반 후보 추출: 하드 필터만 수행.
    """
    qs = Policy.objects.filter(status="ACTIVE")

    # 지역
    profile_sido = getattr(profile, "region_sido", None) or getattr(profile, "region", None)
    if profile_sido:
        qs = qs.filter(
            Q(region_scope="NATIONWIDE")
            | Q(region_sido=profile_sido)
            | Q(applicable_regions__icontains=profile_sido)  # SQLite 호환
        )

    # 연령
    profile_age = getattr(profile, "age", None)
    if profile_age:
        qs = qs.filter(
            Q(min_age__isnull=True) | Q(min_age__lte=profile_age),
            Q(max_age__isnull=True) | Q(max_age__gte=profile_age),
        )

    # 취업 상태 (profile.employment_status -> policy.employment 리스트)
    employment_status = getattr(profile, "employment_status", None)
    if employment_status:
        filtered = qs.filter(employment__icontains=employment_status)  # SQLite 호환
        # 매칭이 전혀 없으면 취업 상태 필터는 건너뛴다 (과도 컷 방지)
        qs = filtered if filtered.exists() else qs

    return qs
