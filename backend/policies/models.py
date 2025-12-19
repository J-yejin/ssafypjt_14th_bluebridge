from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Policy(models.Model):
    source = models.CharField(max_length=30)           # youth / welfare / training / employ
    source_id = models.CharField(max_length=100, unique=True)

    title = models.CharField(max_length=300)
    summary = models.TextField(null=True, blank=True)
    detail_link = models.CharField(max_length=500, null=True, blank=True)

    region_sido = models.CharField(max_length=50, null=True, blank=True)
    region_sigungu = models.CharField(max_length=50, null=True, blank=True)
    region_code = models.CharField(max_length=20, null=True, blank=True)

    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)

    employment_requirements = models.JSONField(default=list, blank=True)
    education_requirements = models.JSONField(default=list, blank=True)
    major_requirements = models.JSONField(default=list, blank=True)

    income_requirements = models.JSONField(default=list, blank=True)
    special_target = models.JSONField(default=list, blank=True)  # 장애인, 보훈대상자 등

    provider = models.CharField(max_length=200, null=True, blank=True)
    apply_method = models.CharField(max_length=200, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)

    raw = models.JSONField()


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
