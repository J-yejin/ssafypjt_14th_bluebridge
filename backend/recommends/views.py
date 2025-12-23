from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from policies.models import Policy
from policies.serializers import PolicyBasicSerializer
from profiles.models import Profile
from .engine import (
    fetch_policies_by_ids,
    search_with_chroma,
    rerank_with_profile,
    assign_ux_scores,
    select_top3_with_reasons,
)
from .models import RecommendationLog


def _normalize_region(region: str) -> str:
    """
    프로필 지역을 광역 시·도 명칭으로 정규화한다.
    """
    if not region:
        return ""
    name = region.strip()
    mapping = {
        "서울": "서울특별시",
        "서울시": "서울특별시",
        "부산": "부산광역시",
        "부산시": "부산광역시",
        "대구": "대구광역시",
        "대구시": "대구광역시",
        "인천": "인천광역시",
        "인천시": "인천광역시",
        "광주": "광주광역시",
        "광주시": "광주광역시",
        "대전": "대전광역시",
        "대전시": "대전광역시",
        "울산": "울산광역시",
        "울산시": "울산광역시",
        "세종": "세종특별자치시",
        "세종시": "세종특별자치시",
        "경기": "경기도",
        "경기도": "경기도",
        "강원": "강원특별자치도",
        "강원도": "강원특별자치도",
        "충북": "충청북도",
        "충북도": "충청북도",
        "충남": "충청남도",
        "충남도": "충청남도",
        "전북": "전라북도",
        "전북도": "전라북도",
        "전남": "전라남도",
        "전남도": "전라남도",
        "경북": "경상북도",
        "경북도": "경상북도",
        "경남": "경상남도",
        "경남도": "경상남도",
        "제주": "제주특별자치도",
        "제주도": "제주특별자치도",
    }
    return mapping.get(name, name)


def _filter_policies_by_profile(qs, profile: Profile):
    """
    기본 추천용 프로필 기반 필터.
    """
    if profile.region:
        target_region = _normalize_region(profile.region)
        # 광역시/도 접두어로도 매칭되도록 보조 문자열을 만든다.
        base_region = (
            target_region.replace("특별자치시", "")
            .replace("특별자치도", "")
            .replace("특별시", "")
            .replace("광역시", "")
            .replace("자치도", "")
            .replace("도", "")
            .strip()
        )
        region_filter = (
            Q(region_scope="NATIONWIDE")
            | Q(region_sido=target_region)
            | Q(region_sido__icontains=target_region)
            | Q(applicable_regions__icontains=target_region)
        )
        if base_region:
            region_filter |= Q(region_sido__icontains=base_region) | Q(
                applicable_regions__icontains=base_region
            )
        qs = qs.filter(region_filter)
    if profile.age:
        qs = qs.filter(
            Q(min_age__isnull=True) | Q(min_age__lte=profile.age),
            Q(max_age__isnull=True) | Q(max_age__gte=profile.age),
        )
    if profile.employment_status:
        qs = qs.filter(employment__icontains=profile.employment_status)
    if profile.major:
        qs = qs.filter(major__icontains=profile.major)
    return qs


def _profile_snapshot(profile: Profile) -> dict:
    """
    추천 로그 저장 시 프로필 주요 필드만 남겨둔다.
    """
    if not profile:
        return {}
    return {
        "age": profile.age,
        "region": profile.region,
        "employment_status": profile.employment_status,
        "major": profile.major,
        "special_targets": profile.special_targets,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommend_list(request):
    """
    GET /bluebridge/recommend/
    프로필 기반 기본 추천(쿼리 없이 필터링 후 간단 정렬).
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    qs = Policy.objects.filter(status="ACTIVE")
    qs = _filter_policies_by_profile(qs, profile)
    # 마감 임박순 기본 정렬
    qs = qs.order_by("end_date")[:10]
    serializer = PolicyBasicSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_detail(request):
    """
    POST /bluebridge/recommend/detail
    ?? + ???? ?? ?? 10? ???? ??.
    body: { "query": "..." }
    """
    query = request.data.get("query")
    if not query:
        return Response({"detail": "query ?? ?????"}, status=400)

    profile, _ = Profile.objects.get_or_create(user=request.user)
    # 더 많은 후보를 확보해 필터 이후에도 결과를 남긴다.
    policy_ids, scores = search_with_chroma(query_text=query, profile=profile, top_k=80)

    qs = Policy.objects.filter(id__in=policy_ids)
    filtered_qs = _filter_policies_by_profile(qs, profile)
    # 필터 적용 후 모두 탈락하면 필터를 완화해 id 매칭만 유지
    if not filtered_qs.exists():
        filtered_qs = qs
    qs = filtered_qs

    policy_map = {p.id: p for p in qs}
    dist_map = {pid: dist for pid, dist in zip(policy_ids, scores)}

    policies = [policy_map[i] for i in policy_ids if i in policy_map]
    filtered_scores = [dist_map.get(p.id, 0.0) for p in policies]

    reranked = rerank_with_profile(policies, filtered_scores, profile)
    reranked = assign_ux_scores(reranked)
    serializer = PolicyBasicSerializer(reranked, many=True)
    ordered_distances = [dist_map.get(p.id) for p in reranked]

    top3 = select_top3_with_reasons(reranked[:10], profile, query)

    try:
        RecommendationLog.objects.create(
            user=request.user,
            query=query,
            profile_snapshot=_profile_snapshot(profile),
            recommended_policy_ids=[p.id for p in reranked],
            ux_scores={str(p.id): getattr(p, "ux_score", None) for p in reranked},
        )
    except Exception:
        pass

    return Response(
        {
            "results": serializer.data,
            "distances": ordered_distances,
            "top3": top3,
        }
    )
