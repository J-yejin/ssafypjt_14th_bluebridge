from django.db import models
from django.contrib.auth.models import User

from policies.models import Policy


class Board(models.Model):
    class Categories(models.TextChoices):
        FREE = "free", "자유"
        REVIEW = "review", "후기"
        QUESTION = "question", "질문"
        NOTICE = "notice", "공지"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=Categories.choices)
    policy = models.ForeignKey(Policy, null=True, blank=True, on_delete=models.SET_NULL, related_name="boards")
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} on {self.board_id}"

# Create your models here.
