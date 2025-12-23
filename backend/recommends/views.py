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


def _filter_policies_by_profile(qs, profile: Profile):
    """
    기본 추천용 프로필 기반 필터.
    """
    if profile.region:
        qs = qs.filter(
            Q(region_scope="NATIONWIDE")
            | Q(region_sido=profile.region)
            | Q(applicable_regions__contains=[profile.region])
        )
    if profile.age:
        qs = qs.filter(
            Q(min_age__isnull=True) | Q(min_age__lte=profile.age),
            Q(max_age__isnull=True) | Q(max_age__gte=profile.age),
        )
    if profile.employment_status:
        qs = qs.filter(employment__contains=[profile.employment_status])
    if profile.major:
        qs = qs.filter(major__contains=[profile.major])
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
    쿼리 임베딩 + 프로필 필터 기반 벡터 검색 상위 10개 반환.
    body: { "query": "텍스트" }
    """
    query = request.data.get("query")
    if not query:
        return Response({"detail": "query 필드가 필요합니다."}, status=400)

    profile, _ = Profile.objects.get_or_create(user=request.user)
    policy_ids, scores = search_with_chroma(query_text=query, profile=profile, top_k=10)
    policies = fetch_policies_by_ids(policy_ids)
    reranked = rerank_with_profile(policies, scores, profile)
    reranked = assign_ux_scores(reranked)
    dist_map = {pid: dist for pid, dist in zip(policy_ids, scores)}
    serializer = PolicyBasicSerializer(reranked, many=True)
    ordered_distances = [dist_map.get(p.id) for p in reranked]

    top3 = select_top3_with_reasons(reranked[:10], profile, query)

    # 추천 로그 저장 (에러는 사용자 응답에 영향 주지 않음)
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
