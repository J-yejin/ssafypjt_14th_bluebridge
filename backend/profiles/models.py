from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    interest = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)  # male/female/other
    household_income = models.PositiveIntegerField(null=True, blank=True)  # 월 소득 (원)
    family_size = models.PositiveIntegerField(null=True, blank=True)       # 가구원 수
    income_quintile = models.CharField(max_length=10, null=True, blank=True)  # 1분위~5분위 계산 결과
    employment_status = models.CharField(max_length=50, null=True, blank=True)  # 취업상태
    education_level = models.CharField(max_length=50, null=True, blank=True)    # 학력
    major = models.CharField(max_length=100, null=True, blank=True)             # 전공
    special_targets = models.JSONField(default=list, blank=True)                # 국가유공자/장애 등 다중 선택

    def __str__(self):
        return f"{self.user.username} Profile"
