from django.db import models
from django.contrib.auth.models import User

# Create your models here. 

class Policy(models.Model):
    # --------------------
    # 1. 식별 / 출처
    # --------------------
    source = models.CharField(
        max_length=30
    )  # youth / welfare / employ / training

    source_id = models.CharField(
        max_length=100
    )

    policy_type = models.CharField(
        max_length=30,
        choices=[
            ("YOUTH", "청년정책"),
            ("WELFARE", "복지서비스"),
            ("TRAINING", "교육/훈련"),
            ("PROGRAM", "프로그램"),
        ],
    )

    # --------------------
    # 2. 기본 정보 (목록/카드)
    # --------------------
    title = models.CharField(max_length=300)

    summary = models.TextField(
        null=True, blank=True
    )  # 출처 제공 요약

    search_summary = models.TextField(
        null=True, blank=True
    )  # 검색/카드 전용 1줄 요약

    keywords = models.JSONField(
        default=list, blank=True
    )  # 정책 키워드, 관심주제 등

    # --------------------
    # 3. 분류 (탐색/필터)
    # --------------------
    category_main = models.CharField(
        max_length=50, null=True, blank=True
    )  # 일자리, 주거, 복지 등

    category_sub = models.CharField(
        max_length=50, null=True, blank=True
    )

    # --------------------
    # 4. 지역 정보
    # --------------------
    region_scope = models.CharField(
        max_length=20,
        choices=[
            ("NATION", "전국"),
            ("LOCAL", "지역"),
        ],
        default="NATION",
    )

    region_sido = models.CharField(
        max_length=50, null=True, blank=True
    )

    region_sigungu = models.CharField(
        max_length=50, null=True, blank=True
    )

    region_codes = models.JSONField(
        default=list, blank=True
    )  # 다중 지역 코드/텍스트

    # --------------------
    # 5. 자격 요건 (핵심)
    # --------------------
    eligibility = models.JSONField(
        default=dict, blank=True
    )
    """
    구조 예시:
    {
      "age": { "min": 19, "max": 34 },
      "employment": ["미취업자"],
      "education": ["고졸 이상"],
      "major": ["제한없음"],
      "income": { "min": null, "max": null },
      "target": ["보훈대상자"],
      "lifecycle": ["청년", "중장년"]
    }
    """

    # --------------------
    # 6. 지원 / 혜택 정보
    # --------------------
    benefit_type = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    # 예: 현금, 교육, 상담, 프로그램, 서비스

    benefit_detail = models.TextField(
        null=True, blank=True
    )

    # --------------------
    # 7. 신청 / 운영 정보
    # --------------------
    provider = models.CharField(
        max_length=200, null=True, blank=True
    )

    apply_method = models.CharField(
        max_length=200, null=True, blank=True
    )

    apply_link = models.CharField(
        max_length=500, null=True, blank=True
    )

    # --------------------
    # 8. 기간 / 상태
    # --------------------
    start_date = models.DateField(
        null=True, blank=True
    )

    end_date = models.DateField(
        null=True, blank=True
    )

    status = models.CharField(
        max_length=20, default="ACTIVE"
    )

    # --------------------
    # 9. 원본 데이터
    # --------------------
    raw = models.JSONField()

    class Meta:
        unique_together = ("source", "source_id")
        indexes = [
            models.Index(fields=["policy_type"]),
            models.Index(fields=["category_main"]),
            models.Index(fields=["region_sido"]),

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "policy"],
                name="unique_user_policy_wishlist",
            ),
        ]
