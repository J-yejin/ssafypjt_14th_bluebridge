from rest_framework import serializers

from boards.models import Board, Comment
from policies.models import Policy


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    board_id = serializers.IntegerField(source="board.id", read_only=True)
    board_title = serializers.CharField(source="board.title", read_only=True)
    board_category = serializers.CharField(source="board.category", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at", "board_id", "board_title", "board_category"]
        read_only_fields = ["id", "user", "created_at", "board_id", "board_title", "board_category"]

class BoardSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
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
            "like_count",
            "is_liked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "views", "created_at", "updated_at"]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()


class BoardDetailSerializer(BoardSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ["comments"]
