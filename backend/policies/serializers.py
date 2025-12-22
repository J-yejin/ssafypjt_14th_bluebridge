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
            "id",
            "source",
            "source_id",
            "title",
            "summary",
            "policy_detail",
            "detail_link",
            "detail_contact",
            "region_scope",
            "region_sido",
            "region_sigungu",
            "applicable_regions",
            "min_age",
            "max_age",
            "employment_requirements",
            "education_requirements",
            "major_requirements",
            "target_detail",
            "special_target",
            "provider",
            "apply_method",
            "start_date",
            "end_date",
            "status",
            "category",
            "keywords",
            "policy_type",
        ]

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


class PolicyBasicSerializer(serializers.ModelSerializer):
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
