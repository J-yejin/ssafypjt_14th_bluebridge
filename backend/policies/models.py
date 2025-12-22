from django.db import models
from django.contrib.auth.models import User

class Policy(models.Model):
    # =========================
    # 1. 식별 / 출처
    # =========================
    source = models.CharField(max_length=30)
    source_id = models.CharField(max_length=100)

    # =========================
    # 2. 필터 ① 정책 유형 (필수)
    # =========================
    policy_type = models.CharField(
        max_length=30,
        choices=[("YOUTH", "청년정책"), ("WELFARE", "복지서비스")]
    )

    # =========================
    # 3. 기본 정보
    # =========================
    title = models.CharField(max_length=300)
    summary = models.TextField(null=True, blank=True)
    search_summary = models.TextField(null=True, blank=True)  # 검색 전용
    keywords = models.JSONField(default=list, blank=True)

    # =========================
    # 4. 필터 ② 카테고리
    # =========================
    category = models.CharField(max_length=50, null=True, blank=True)
    # 일자리 / 주거 / 교육 / 금융 / 복지 / 기타 
    
    # =========================
    # 5. 필터 ③ 지역 (필수)
    # =========================
    region_scope = models.CharField(
        max_length=20,
        choices=[("NATIONWIDE", "전국"), ("LOCAL", "지역")],
        default="NATIONWIDE"
    )  # 전국 정책인가, 지역 정책인가
    region_sido = models.CharField(max_length=50, null=True, blank=True)  # 시/도 단위, 필터 기준
    region_sigungu = models.CharField(max_length=50, null=True, blank=True) # 시/군/구 단위, 대표 지역
    applicable_regions = models.JSONField(default=list, blank=True)  # 실제로 적용 가능한 모든 지역 (텍스트, 다중)

    # =========================
    # 6. 필터 ④ 연령 (필수)
    # =========================
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)

    # =========================
    # 7. 필터 ⑤ 취업 상태 (선택)
    # =========================
    employment = models.JSONField(default=list, blank=True)
    # ["미취업자", "재직자"]

    # =========================
    # 8. 조건 정보 (UI 표시용)
    # =========================
    education = models.JSONField(default=list, blank=True)
    major = models.JSONField(default=list, blank=True)
    special_target = models.JSONField(default=list, blank=True)
    target_detail = models.JSONField(default=list, blank=True)
    
    # =========================
    # 9. 운영 / 지원 정보
    # =========================
    provider = models.CharField(max_length=200, null=True, blank=True)
    apply_method = models.TextField(null=True, blank=True)
    detail_links = models.JSONField(default=list, blank=True)
    detail_contact = models.JSONField(default=list, blank=True)

    service_type = models.CharField(max_length=50, null=True, blank=True) # 현금 / 교육 / 서비스 등
    policy_detail = models.TextField(null=True, blank=True)

    # =========================
    # 10. 필터 ⑥ 신청 가능 여부 (선택)
    # =========================
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # =========================
    # 11. 상태 / 원본
    # =========================
    status = models.CharField(max_length=20, default="ACTIVE")
    raw = models.JSONField()

    class Meta:
        unique_together = ("source", "source_id")
        indexes = [
            models.Index(fields=["policy_type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["region_sido"]),
        ]

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
