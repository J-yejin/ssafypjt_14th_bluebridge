from rest_framework import serializers
from policies.models import Policy

# 정책 모델 serializer
class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "id",

            # 출처
            "source",
            "source_id",

            # 기본 정보
            "title",
            "summary",
            "detail_link",

            # 지역
            "region_sido",
            "region_sigungu",
            "region_code",

            # 연령
            "min_age",
            "max_age",

            # 조건
            "employment_requirements",
            "education_requirements",
            "major_requirements",
            "income_requirements",
            "special_target",

            # 기관 / 신청
            "provider",
            "apply_method",

            # 기간
            "start_date",
            "end_date",

            # 상태
            "status",
        ]


# 정책 검색용 serialzier
class PolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "id",
            "title",
            "summary",
            "source_type",
            "region",
            "category",
            "end_date",
        ]
