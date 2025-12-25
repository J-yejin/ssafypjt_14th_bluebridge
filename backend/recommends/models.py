from django.conf import settings
from django.db import models


class RecommendationLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_logs",
    )
    query = models.TextField(null=True, blank=True)
    profile_snapshot = models.JSONField(default=dict, blank=True)
    recommended_policy_ids = models.JSONField(default=list)
    ux_scores = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"RecommendationLog(user={self.user_id}, query={self.query})"
