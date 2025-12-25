from django.db.models import Count, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from boards.models import Board, BoardLike, Comment
from boards.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    CommentSerializer,
)


def paginate_queryset(queryset, page, page_size):
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]


def parse_positive_int(value, default):
    try:
        value_int = int(value)
        return value_int if value_int > 0 else default
    except (TypeError, ValueError):
        return default


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def board_list(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=401)

        serializer = BoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    category = request.query_params.get("category")
    page = parse_positive_int(request.query_params.get("page"), 1)
    page_size = parse_positive_int(request.query_params.get("page_size"), 10)

    qs = (
        Board.objects.all()
        .select_related("user", "policy")
        .annotate(like_count=Count("likes", distinct=True))
        .order_by("-created_at")
    )
    if category:
        qs = qs.filter(category=category)

    total = qs.count()
    paginated = paginate_queryset(qs, page, page_size)
    serializer = BoardSerializer(paginated, many=True, context={"request": request})
    return Response(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])
def board_detail(request, pk):
    board = get_object_or_404(
        Board.objects.select_related("user", "policy").annotate(like_count=Count("likes", distinct=True)),
        pk=pk,
    )

    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=401)
        Board.objects.filter(pk=board.pk).update(views=F("views") + 1)
        board.refresh_from_db()
        serializer = BoardDetailSerializer(board, context={"request": request})
        return Response(serializer.data)

    if not request.user.is_authenticated or board.user != request.user:
        return Response({"detail": "Permission denied"}, status=403)

    if request.method == "PUT":
        serializer = BoardSerializer(board, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    board.delete()
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_comment(request, pk):
    board = get_object_or_404(Board, pk=pk)
    serializer = CommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user, board=board)
    return Response(serializer.data, status=201)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user != request.user:
        return Response({"detail": "Permission denied"}, status=403)
    comment.delete()
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_like(request, pk):
    board = get_object_or_404(Board, pk=pk)
    like, created = BoardLike.objects.get_or_create(board=board, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    like_count = BoardLike.objects.filter(board=board).count()
    return Response({"liked": liked, "like_count": like_count})
