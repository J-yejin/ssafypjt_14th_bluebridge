from rest_framework import serializers

from boards.models import Board, Comment
from policies.models import Policy


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class BoardSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    policy = serializers.PrimaryKeyRelatedField(
        queryset=Policy.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "user",
            "title",
            "content",
            "category",
            "policy",
            "views",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "views", "created_at", "updated_at"]


class BoardDetailSerializer(BoardSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ["comments"]
