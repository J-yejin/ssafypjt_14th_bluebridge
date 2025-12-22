from rest_framework import serializers
from .models import Profile


def calculate_income_quintile(household_income, family_size):
    """
    간단한 소득분위 계산기.
    - 입력: 월 소득(household_income, 원), 가구원 수(family_size)
    - 출력: "1분위" ~ "5분위" 문자열 또는 None
    """
    if not household_income or not family_size:
        return None

    median_income_by_size = {
        1: 2392013,
        2: 3932658,
        3: 5025353,
        4: 6097773,
        5: 7108192,
        6: 8064805,
        7: 8988428,
    }

    median_income = median_income_by_size.get(family_size)
    if not median_income:
        return None

    income_percentage = (household_income / median_income) * 100

    if income_percentage < 20:
        return "1분위"
    elif income_percentage < 40:
        return "2분위"
    elif income_percentage < 60:
        return "3분위"
    elif income_percentage < 80:
        return "4분위"
    return "5분위"


class ProfileSerializer(serializers.ModelSerializer):
    income_quintile = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'age',
            'region',
            'interest',
            'gender',
            'household_income',
            'family_size',
            'income_quintile',
            'employment_status',
            'education_level',
            'major',
            'special_targets',
        )

    def validate(self, attrs):
        # 기존 값과 병합 후 계산 (partial update 고려)
        instance = getattr(self, "instance", None)
        income = attrs.get("household_income", getattr(instance, "household_income", None))
        family_size = attrs.get("family_size", getattr(instance, "family_size", None))
        attrs["income_quintile"] = calculate_income_quintile(income, family_size)
        return attrs
