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

QUERY_EXAMPLES = [
    "청년 창업 초기 장비 구입비 지원하는 사업 있어?",
    "서울 거주 대학원생 등록금·장학금 지원 제도 알려줘",
    "다자녀 가구 전기요금·교통비 할인 정책 찾아줘",
    "장애인 보조기기 대여나 수리비 지원 프로그램 있나요?",
    "군 전역 예정자 직업훈련 바우처/교육비 지원 사업 추천해줘",
    "농어업인 재해보험이나 경영안정 자금 지원 정책 찾아줘",
    "신혼부부 전세자금 대출 이자 지원 정책 알려줘",
    "저소득층 의료비나 건강검진 바우처 지원 사업 뭐가 있지?",
]


def _build_profile_query(profile: Profile) -> str:
    """프로필 정보를 텍스트 질의로 만들어 유사도 검색에 활용."""
    if not profile:
        return ""
    parts = []
    if profile.region:
        parts.append(f"{profile.region} 거주")
    if profile.age:
        parts.append(f"{profile.age}세")
    if profile.gender:
        parts.append(profile.gender)
    if profile.employment_status:
        parts.append(profile.employment_status)
    if profile.education_level:
        parts.append(profile.education_level)
    if profile.major:
        parts.append(profile.major)
    if profile.income_quintile:
        parts.append(f"소득분위 {profile.income_quintile}")
    if profile.interest:
        parts.append(profile.interest)
    if profile.special_targets:
        parts.extend(profile.special_targets)
    return " ".join([p for p in parts if p])


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
    프로필 기반 맞춤 추천을 하이브리드 검색으로 반환.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    query_text = _build_profile_query(profile) or "맞춤 정책 추천"

    policy_ids, scores = search_with_chroma(query_text=query_text, profile=profile, top_k=10)
    policies = fetch_policies_by_ids(policy_ids)
    # 프로필 피드: 프로필 점수 중심으로 정렬 (쿼리 유사도 영향 최소화)
    reranked = rerank_with_profile(policies, scores, profile, weight_profile=1.0, weight_similarity=0.0)
    reranked = assign_ux_scores(reranked)

    dist_map = {pid: dist for pid, dist in zip(policy_ids, scores)}
    serializer = PolicyBasicSerializer(reranked, many=True)
    ordered_distances = [dist_map.get(p.id) for p in reranked]

    top3_raw = select_top3_with_reasons(reranked[:10], profile, query_text)
    reason_map = {item.get("id"): item.get("reason") for item in top3_raw}
    top3_cards = []
    for p in reranked[:3]:
        top3_cards.append(
            {
                "id": p.id,
                "title": p.title,
                "ux_score": getattr(p, "ux_score", None),
                "similarity_score_10": getattr(p, "similarity_score_10", None),
                "profile_score_10": getattr(p, "profile_score_10", None),
                "policy_target_required": getattr(p, "policy_target_required", False),
                "policy_target_match": getattr(p, "policy_target_match", None),
                "reason": reason_map.get(p.id),
            }
        )

    return Response(
        {
            "results": serializer.data,
            "distances": ordered_distances,
            "top3": top3_cards,
            "query_examples": QUERY_EXAMPLES,
            "echo_query": query_text,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_detail(request):
    """
    POST /bluebridge/recommend/detail
    질의 + 프로필 기반 벡터 검색 결과 10개와 Top3 이유.
    body: { "query": "..." }
    """
    query = request.data.get("query")
    if not query:
        return Response({"detail": "query 필드가 비어있습니다"}, status=400)

    profile, _ = Profile.objects.get_or_create(user=request.user)
    policy_ids, scores = search_with_chroma(query_text=query, profile=profile, top_k=10)
    policies = fetch_policies_by_ids(policy_ids)
    # 검색 모드: 유사도 우선, 프로필은 보조
    reranked = rerank_with_profile(policies, scores, profile, weight_profile=0.2, weight_similarity=0.8)
    reranked = assign_ux_scores(reranked)

    dist_map = {pid: dist for pid, dist in zip(policy_ids, scores)}
    serializer = PolicyBasicSerializer(reranked, many=True)
    ordered_distances = [dist_map.get(p.id) for p in reranked]

    top3_raw = select_top3_with_reasons(reranked[:10], profile, query)
    reason_map = {item.get("id"): item.get("reason") for item in top3_raw}
    top3_cards = []
    for p in reranked[:3]:
        top3_cards.append(
            {
                "id": p.id,
                "title": p.title,
                "ux_score": getattr(p, "ux_score", None),
                "similarity_score_10": getattr(p, "similarity_score_10", None),
                "profile_score_10": getattr(p, "profile_score_10", None),
                "policy_target_required": getattr(p, "policy_target_required", False),
                "policy_target_match": getattr(p, "policy_target_match", None),
                "reason": reason_map.get(p.id),
            }
        )

    try:
        RecommendationLog.objects.create(
            user=request.user,
            query=query,
            profile_snapshot=_profile_snapshot(profile),
            recommended_policy_ids=[p.id for p in reranked],
            ux_scores={
                str(p.id): {
                    "ux": getattr(p, "ux_score", None),
                    "sim10": getattr(p, "similarity_score_10", None),
                    "profile10": getattr(p, "profile_score_10", None),
                    "policy_target_required": getattr(p, "policy_target_required", False),
                    "policy_target_match": getattr(p, "policy_target_match", None),
                }
                for p in reranked
            },
        )
    except Exception:
        pass

    return Response(
        {
            "results": serializer.data,
            "distances": ordered_distances,
            "top3": top3_cards,
            "echo_query": query,
        }
    )
