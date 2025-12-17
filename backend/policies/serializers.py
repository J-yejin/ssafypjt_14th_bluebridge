from rest_framework import serializers
from .models import Policy, PolicyEligibility, PolicyRegion


class PolicyRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyRegion
        fields = ['sido_code', 'sigungu_code', 'sido_name', 'sigungu_name']


class PolicyEligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyEligibility
        exclude = ['id', 'policy']


class PolicySerializer(serializers.ModelSerializer):
    eligibility = PolicyEligibilitySerializer(read_only=True)
    regions = PolicyRegionSerializer(many=True, read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id',
            'source',
            'category',
            'title',
            'description',
            'application_start',
            'application_end',
            'is_active',
            'eligibility',
            'regions',
        ]
