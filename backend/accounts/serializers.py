from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from profiles.models import Profile 
from profiles.serializers import calculate_income_quintile


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    age = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    region = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    interest = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    household_income = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    family_size = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    employment_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    education_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    major = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    special_targets = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password_confirm",
            "age",
            "region",
            "interest",
            "gender",
            "household_income",
            "family_size",
            "employment_status",
            "education_level",
            "major",
            "special_targets",
        )

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # remove non-user fields
        password_confirm = validated_data.pop("password_confirm")
        age = validated_data.pop("age", None)
        region = validated_data.pop("region", None)
        interest = validated_data.pop("interest", None)
        gender = validated_data.pop("gender", None)
        household_income = validated_data.pop("household_income", None)
        family_size = validated_data.pop("family_size", None)
        employment_status = validated_data.pop("employment_status", None)
        education_level = validated_data.pop("education_level", None)
        major = validated_data.pop("major", None)
        special_targets = validated_data.pop("special_targets", [])

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )

        quintile = calculate_income_quintile(household_income, family_size)
        Profile.objects.create(
            user=user,
            age=age,
            region=region,
            interest=interest,
            gender=gender,
            household_income=household_income,
            family_size=family_size,
            income_quintile=quintile,
            employment_status=employment_status,
            education_level=education_level,
            major=major,
            special_targets=special_targets,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"]
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data
