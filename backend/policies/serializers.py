from rest_framework import serializers
from policies.models import Policy, Wishlist

# 정책 모델 serializer
from rest_framework import serializers
from .models import Policy


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            # =========================
            # 식별 / 출처
            # =========================
            "id",
            "source",
            "source_id",
            "policy_type",

            # =========================
            # 기본 정보
            # =========================
            "title",
            "summary",
            "search_summary",
            "keywords",

            # =========================
            # 카테고리
            # =========================
            "category",

            # =========================
            # 지역
            # =========================
            "region_scope",
            "region_sido",
            "region_sigungu",
            "applicable_regions",

            # =========================
            # 연령
            # =========================
            "min_age",
            "max_age",

            # =========================
            # 취업 상태
            # =========================
            "employment",

            # =========================
            # 조건 정보 (UI 표시용)
            # =========================
            "education",
            "major",
            "special_target",
            "target_detail",

            # =========================
            # 운영 / 지원 정보
            # =========================
            "provider",
            "apply_method",
            "detail_links",
            "detail_contact",

            "service_type",
            "policy_detail",

            # =========================
            # 신청 기간
            # =========================
            "start_date",
            "end_date",

            # =========================
            # 상태
            # =========================
            "status",
        ]

        read_only_fields = fields



# 정책 검색용 serialzier
class PolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "id",
            "policy_type",

            "title",
            "search_summary",

            "category",

            "region_scope",
            "region_sido",

            "min_age",
            "max_age",

            "provider",

            "benefit_type",

            "status",
        ]
        read_only_fields = fields



class PolicyBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "id",
            "title",
            "summary",
            "source",
            "region_sido",
            "region_sigungu",
            "end_date",
            "status",
        ]


class WishlistCreateSerializer(serializers.ModelSerializer):
    policy_id = serializers.PrimaryKeyRelatedField(
        queryset=Policy.objects.all(),
        source="policy",
        write_only=True,
    )

    class Meta:
        model = Wishlist
        fields = ["policy_id"]


class WishlistItemSerializer(serializers.ModelSerializer):
    policy = PolicyBasicSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "policy", "created_at"]
