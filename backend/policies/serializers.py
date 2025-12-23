from rest_framework import serializers

from policies.models import Policy, Wishlist


def _list_or_empty(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


class PolicySerializer(serializers.ModelSerializer):
    detail_link = serializers.SerializerMethodField()
    employment_requirements = serializers.SerializerMethodField()
    education_requirements = serializers.SerializerMethodField()
    major_requirements = serializers.SerializerMethodField()
    special_target = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = [
            # 식별 / 출처
            "id",
            "source",
            "source_id",
            "policy_type",
            # 기본 정보
            "title",
            "summary",
            "policy_detail",
            "search_summary",
            "keywords",
            # 카테고리
            "category",
            # 지역
            "region_scope",
            "region_sido",
            "region_sigungu",
            "applicable_regions",
            # 연령
            "min_age",
            "max_age",
            # 취업/조건 정보
            "employment_requirements",
            "education_requirements",
            "major_requirements",
            "special_target",
            "target_detail",
            # 운영/지원 정보
            "provider",
            "apply_method",
            "detail_link",
            "detail_links",
            "detail_contact",
            "service_type",
            # 신청 기간
            "start_date",
            "end_date",
            # 상태
            "status",
        ]
        read_only_fields = fields

    def get_detail_link(self, obj):
        links = getattr(obj, "detail_links", None)
        if isinstance(links, list) and links:
            return links[0]
        return None

    def get_employment_requirements(self, obj):
        return _list_or_empty(getattr(obj, "employment", []))

    def get_education_requirements(self, obj):
        return _list_or_empty(getattr(obj, "education", []))

    def get_major_requirements(self, obj):
        return _list_or_empty(getattr(obj, "major", []))

    def get_special_target(self, obj):
        base = _list_or_empty(getattr(obj, "special_target", []))
        detail = _list_or_empty(getattr(obj, "target_detail", []))
        return base + detail


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
            "status",
        ]
        read_only_fields = fields


class PolicyBasicSerializer(serializers.ModelSerializer):
    ux_score = serializers.IntegerField(read_only=True, default=None)
    profile_score = serializers.FloatField(read_only=True, default=None)
    query_similarity = serializers.FloatField(read_only=True, default=None)
    detail_link = serializers.SerializerMethodField()

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
            "ux_score",
            "profile_score",
            "query_similarity",
            "detail_link",
        ]

    def get_detail_link(self, obj):
        links = getattr(obj, "detail_links", None)
        if isinstance(links, list) and links:
            return links[0]
        return None


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
