from django.shortcuts import render

# Create your views here.
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .models import Policy
from .serializers import PolicySerializer

# 정책 리스트 조회 : 초기 화면 - 랜덤으로 20개 보여줌
@api_view(["GET"])
def policy_list(request):
    qs = Policy.objects.all()
    total = qs.count()

    if total <= 20:
        policies = qs
    else:
        random_ids = random.sample(
            list(qs.values_list("id", flat=True)),
            20
        )
        policies = qs.filter(id__in=random_ids)

    serializer = PolicySerializer(policies, many=True)
    return Response(serializer.data)

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
    - 검색 = 필터의 한 형태
    - 랜덤 없음
    - 조건 기반 deterministic 결과
    """
    qs = Policy.objects.all()

    # 1️⃣ 상태 필터 (기본값)
    status = request.query_params.get("status")
    if status:
        qs = qs.filter(status=status)

    # 2️⃣ 검색어 (q)
    q = request.query_params.get("q")
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(summary__icontains=q) |
            Q(provider__icontains=q)
        )

    # 3️⃣ 출처 필터
    source = request.query_params.get("source")
    if source:
        qs = qs.filter(source=source)

    # 4️⃣ 지역 필터
    region_sido = request.query_params.get("region_sido")
    if region_sido:
        qs = qs.filter(region_sido=region_sido)

    region_sigungu = request.query_params.get("region_sigungu")
    if region_sigungu:
        qs = qs.filter(region_sigungu=region_sigungu)

    # 5️⃣ 정렬
    ordering = request.query_params.get("ordering", "deadline")
    if ordering == "latest":
        qs = qs.order_by("-start_date")
    elif ordering == "name":
        qs = qs.order_by("title")
    else:
        # 기본: 마감 임박순 (null은 뒤로)
        qs = qs.order_by("end_date")

    # 6️⃣ 페이징
    paginator = PolicySearchPagination()
    page = paginator.paginate_queryset(qs, request)

    serializer = PolicySerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
