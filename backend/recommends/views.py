from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from profiles.models import Profile
from .models import RecommendationLog
from .profile_engine import profile_recommend
from .query_engine import query_recommend

QUERY_EXAMPLES = [
    "분야:창업 | 대상:청년 | 혜택:장비 구입비 지원",
    "분야:교육 | 대상:대학원생 | 혜택:등록금·장학금",
    "분야:주거 | 대상:청년 | 혜택:전세/월세 대출·이자지원",
    "분야:보건 | 대상:저소득 | 혜택:의료비/건강검진 바우처",
    "분야:취업 | 대상:군 전역 예정자 | 혜택:직업훈련 바우처",
]


def _profile_snapshot(profile: Profile) -> dict:
    """추천 로그에 남길 주요 프로필 스냅샷."""
    if not profile:
        return {}
    return {
        "age": profile.age,
        "region": profile.region,
        "gender": profile.gender,
        "employment_status": profile.employment_status,
        "education_level": profile.education_level,
        "income_quintile": profile.income_quintile,
        "major": profile.major,
        "interest": profile.interest,
        "special_targets": profile.special_targets,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommend_list(request):
    """
    GET /bluebridge/recommend/
    프로필 기반 맞춤 추천 (DB + 점수 기반).
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    recommended = profile_recommend(user=request.user)
    recommended_ids = [item["policy_id"] for item in recommended]

    RecommendationLog.objects.create(
        user=request.user,
        query=None,
        profile_snapshot=_profile_snapshot(profile),
        recommended_policy_ids=recommended_ids,
        ux_scores={},
    )

    return Response(
        {
            "type": "profile",
            "results": recommended,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_detail(request):
    """
    POST /bluebridge/recommend/detail
    질의 기반 추천 (DB 검색 기반).
    body: { "query": "..." }
    """
    query = request.data.get("query")
    if not query:
        return Response({"detail": "query 필드가 비어있습니다"}, status=400)

    results = query_recommend(query=query, user=request.user)
    recommended_ids = [item["policy_id"] for item in results]

    RecommendationLog.objects.create(
        user=request.user,
        query=query,
        profile_snapshot=_profile_snapshot(getattr(request.user, "profile", None)),
        recommended_policy_ids=recommended_ids,
        ux_scores={},
    )

    return Response(
        {
            "type": "query",
            "query": query,
            "results": results,
            "query_examples": QUERY_EXAMPLES,
        }
    )
