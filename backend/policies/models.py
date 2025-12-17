from django.db import models

# 모든 정책의 공통 베이스(온통청년 / 복지로 / 워크넷 등)
class Policy(models.Model):


    SOURCE_CHOICES = [
        ('YOUTH', '온통청년'),
        ('WELFARE', '복지로'),
        ('WORKNET', '워크넷'),
    ]

    CATEGORY_CHOICES = [
        ('JOB', '일자리'),
        ('EDU', '교육/훈련'),
        ('HOUSING', '주거'),
        ('WELFARE', '복지'),
        ('FINANCE', '금융'),
        ('ETC', '기타'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    application_start = models.DateField(null=True, blank=True)
    application_end = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_source_display()}] {self.title}"
    
# 정책 대상 조건 (추천 필터 핵심)
class PolicyEligibility(models.Model):


    policy = models.OneToOneField(
        Policy,
        on_delete=models.CASCADE,
        related_name='eligibility'
    )

    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)

    employment_status = models.CharField(
        max_length=50,
        blank=True,
        help_text="미취업, 재직, 구직중, 자영업 등"
    )

    education_level = models.CharField(
        max_length=50,
        blank=True,
        help_text="고졸, 대재, 대졸, 대학원 등"
    )

    income_min = models.PositiveIntegerField(null=True, blank=True)
    income_max = models.PositiveIntegerField(null=True, blank=True)

    requires_business_registration = models.BooleanField(
        null=True, blank=True,
        help_text="사업자등록 필요 여부"
    )

    special_target = models.CharField(
        max_length=100,
        blank=True,
        help_text="장애인, 보훈대상자, 차상위 등"
    )

# 정책 적용 지역
class PolicyRegion(models.Model):
    """
    
    """

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='regions'
    )

    sido_code = models.CharField(max_length=10)
    sigungu_code = models.CharField(max_length=10, blank=True)

    sido_name = models.CharField(max_length=50)
    sigungu_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.sido_name} {self.sigungu_name}".strip()

# 교육/훈련 (내일배움카드, 워크넷)
class TrainingPolicyDetail(models.Model):
    policy = models.OneToOneField(
        Policy,
        on_delete=models.CASCADE,
        related_name='training_detail'
    )

    institution_name = models.CharField(max_length=255, blank=True)
    training_field = models.CharField(max_length=255, blank=True)
    certificate = models.CharField(max_length=255, blank=True)

# 복지 정책
class WelfarePolicyDetail(models.Model):
    policy = models.OneToOneField(
        Policy,
        on_delete=models.CASCADE,
        related_name='welfare_detail'
    )

    benefit_type = models.CharField(max_length=100, blank=True)
    benefit_amount = models.CharField(max_length=100, blank=True)
