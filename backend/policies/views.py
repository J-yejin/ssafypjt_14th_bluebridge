from django.shortcuts import render

# Create your views here.
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import date

from .models import Policy, Wishlist
from .serializers import PolicySerializer, PolicyListSerializer, WishlistCreateSerializer, WishlistItemSerializer

# 정책 리스트 조회 : 기본 리스트 (페이지네이션, 랜덤 아님)
@api_view(["GET"])
def policy_list(request):
    qs = Policy.objects.filter(status="ACTIVE")

    # 검색어
    q = request.query_params.get("q")
    if q:
        qs = qs.filter(search_summary__icontains=q)

    # 카테고리
    category = request.query_params.get("category")
    if category:
        # 매핑된 버킷 이름과 원본 카테고리 키워드를 모두 검색
        bucket = category.strip()
        synonyms = {
            "일자리": ["일자리", "취업", "창업"],
            "교육": ["교육"],
            "복지문화": ["복지문화", "문화", "문화·여가", "문화여가"],
            "건강": ["건강", "신체건강", "정신건강"],
            "생활지원": ["생활지원", "보육", "돌봄", "보호·돌봄", "주거"],
            "재무/법률": ["재무", "법률", "서민금융", "재무/법률"],
            "위기·안전": ["위기", "안전", "위기·안전"],
            "가족/권리": ["가족", "권리", "임신·출산", "입양·위탁", "참여권리"],
            "기타": ["기타"],
        }
        keys = synonyms.get(bucket, [bucket])
        q_obj = Q()
        for key in keys:
            q_obj |= Q(category__icontains=key)
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
def policy_detail(request, id):
    try:
        policy = Policy.objects.get(id=id)
    except Policy.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    serializer = PolicySerializer(policy)
    return Response(serializer.data)

# 정책 검색 : 페이지네이션
class PolicySearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

'''
검색은 title·summary·provider 중심의 부분 일치 검색과
source·지역·상태 필터를 결합한 deterministic한 API로 설계
'''

@api_view(["GET"])
def policy_search(request):
    """
    정책 검색 API
    - 검색(q): search_summary 기반
    - 필터: policy_type / category / region / age / employment / 신청 가능 여부
    - deterministic
    """
    qs = Policy.objects.all()

    # =========================
    # 1. 상태 (기본 필터)
    # =========================
    status = request.query_params.get("status", "ACTIVE")
    qs = qs.filter(status=status)

    # =========================
    # 2. 검색어 (q)
    # =========================
    q = request.query_params.get("q")
    if q:
        qs = qs.filter(search_summary__icontains=q)

    # =========================
    # 3. 정책 유형 필터
    # =========================
    policy_type = request.query_params.get("policy_type")
    if policy_type:
        qs = qs.filter(policy_type=policy_type)

    # =========================
    # 4. 카테고리 필터
    # =========================
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category=category)

    # =========================
    # 5. 지역 필터
    # =========================
    region_sido = request.query_params.get("region_sido")
    if region_sido:
        qs = qs.filter(
            Q(region_scope="NATIONWIDE") |
            Q(region_sido=region_sido) |
            Q(applicable_regions__contains=[region_sido])
        )

    region_sigungu = request.query_params.get("region_sigungu")
    if region_sigungu:
        qs = qs.filter(region_sigungu=region_sigungu)

    # =========================
    # 6. 연령 필터
    # =========================
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

    # =========================
    # 7. 취업 상태 필터
    # =========================
    employment = request.query_params.get("employment")
    if employment:
        qs = qs.filter(employment__contains=[employment])

    # =========================
    # 8. 신청 가능 여부 필터
    # =========================
    is_open = request.query_params.get("is_open")
    if is_open == "true":
        today = date.today()
        qs = qs.filter(
            Q(start_date__isnull=True) | Q(start_date__lte=today),
            Q(end_date__isnull=True) | Q(end_date__gte=today),
        )

    # =========================
    # 9. 정렬
    # =========================
    ordering = request.query_params.get("ordering", "deadline")
    if ordering == "latest":
        qs = qs.order_by("-start_date")
    elif ordering == "name":
        qs = qs.order_by("title")
    else:
        qs = qs.order_by("end_date")

    # =========================
    # 10. 페이징
    # =========================
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
