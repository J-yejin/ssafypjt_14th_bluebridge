from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Policy, Wishlist
from .serializers import (
    PolicySerializer,
    PolicyListSerializer,
    WishlistCreateSerializer,
    WishlistItemSerializer,
)


# 정책 리스트 조회 : 기본 리스트(페이지네이션 포함)
@api_view(["GET"])
@permission_classes([AllowAny])
def policy_list(request):
    qs = Policy.objects.filter(status="ACTIVE")

    # 검색어
    q = request.query_params.get("q")
    if q:
        qs = qs.filter(search_summary__icontains=q)

    # 카테고리 (콤마로 구분된 복수 값 지원)
    category = request.query_params.get("category")
    if category:
        buckets = [c.strip() for c in category.split(",") if c.strip()]

        synonyms = {
            "일자리": ["일자리", "취업", "창업", "근로", "고용", "창직"],
            "교육": ["교육", "훈련", "강의", "연수"],
            "복지/문화": ["복지", "문화", "여가", "체육", "생활"],
            "건강": ["건강", "보건", "의료"],
            "생활지원": ["생활지원", "주거", "주택", "주거비", "생활안정"],
            "재무/법률": ["재무", "법률", "서민금융", "금융", "신용", "대출", "융자", "채무"],
            "위기·안전": ["위기", "안전", "재난", "재해", "치안"],
            "가족/권리": ["가족", "권리", "육아", "양육", "돌봄"],
            "기타": ["기타"],
        }

        q_obj = Q()
        for bucket in buckets:
            keys = synonyms.get(bucket, [bucket])
            for key in keys:
                q_obj |= Q(category__icontains=key)
        if q_obj:
            qs = qs.filter(q_obj)

    # 지역(시도) - 전국 포함
    region = request.query_params.get("region")
    if region:
        qs = qs.filter(Q(region_scope="NATIONWIDE") | Q(region_sido=region))

    # 정렬
    ordering = request.query_params.get("ordering", "-id")
    qs = qs.order_by(ordering)

    paginator = PolicySearchPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = PolicyListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


# 정책 상세 조회
@api_view(["GET"])
@permission_classes([AllowAny])
def policy_detail(request, id):
    try:
        policy = Policy.objects.get(id=id)
    except Policy.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    serializer = PolicySerializer(policy)
    return Response(serializer.data)


# 정책 검색 : 페이지네이션 포함
class PolicySearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


@api_view(["GET"])
@permission_classes([AllowAny])
def policy_search(request):
    """
    정책 검색 API
    - 검색(q): search_summary 기반
    - 필터: policy_type / category / region / age / employment / 진행 여부
    - deterministic
    """
    qs = Policy.objects.all()

    # 상태(기본 ACTIVE)
    status = request.query_params.get("status", "ACTIVE")
    qs = qs.filter(status=status)

    # 검색어
    q = request.query_params.get("q")
    if q:
        qs = qs.filter(search_summary__icontains=q)

    # 정책 유형
    policy_type = request.query_params.get("policy_type")
    if policy_type:
        qs = qs.filter(policy_type=policy_type)

    # 카테고리
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category=category)

    # 지역
    region_sido = request.query_params.get("region_sido")
    if region_sido:
        qs = qs.filter(
            Q(region_scope="NATIONWIDE")
            | Q(region_sido=region_sido)
            | Q(applicable_regions__contains=[region_sido])
        )

    region_sigungu = request.query_params.get("region_sigungu")
    if region_sigungu:
        qs = qs.filter(region_sigungu=region_sigungu)

    # 연령
    age = request.query_params.get("age")
    if age:
        try:
            age = int(age)
            qs = qs.filter(
                Q(min_age__isnull=True) | Q(min_age__lte=age),
                Q(max_age__isnull=True) | Q(max_age__gte=age),
            )
        except ValueError:
            pass

    # 취업 상태
    employment = request.query_params.get("employment")
    if employment:
        qs = qs.filter(employment__contains=[employment])

    # 진행 여부(오늘 기준)
    is_open = request.query_params.get("is_open")
    if is_open == "true":
        today = date.today()
        qs = qs.filter(
            Q(start_date__isnull=True) | Q(start_date__lte=today),
            Q(end_date__isnull=True) | Q(end_date__gte=today),
        )

    # 정렬
    ordering = request.query_params.get("ordering", "deadline")
    if ordering == "latest":
        qs = qs.order_by("-start_date")
    elif ordering == "name":
        qs = qs.order_by("title")
    else:
        qs = qs.order_by("end_date")

    paginator = PolicySearchPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = PolicyListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def wishlist_list_create(request):
    if request.method == "POST":
        serializer = WishlistCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        policy = serializer.validated_data["policy"]

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            policy=policy,
        )
        if not created:
            return Response({"detail": "Already wishlisted"}, status=400)

        output = WishlistItemSerializer(wishlist)
        return Response(output.data, status=201)

    qs = Wishlist.objects.filter(user=request.user).select_related("policy")
    serializer = WishlistItemSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def wishlist_delete(request, policy_id):
    wishlist = get_object_or_404(
        Wishlist,
        user=request.user,
        policy_id=policy_id,
    )
    wishlist.delete()
    return Response(status=204)