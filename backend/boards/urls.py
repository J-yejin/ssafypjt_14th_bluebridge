from django.urls import path

from boards import views

urlpatterns = [
    path("", views.board_list, name="board-list"),
    path("<int:pk>/", views.board_detail, name="board-detail"),
    path("<int:pk>/like/", views.toggle_like, name="board-like"),
    path("<int:pk>/comments/", views.create_comment, name="comment-create"),
    path("comments/me/", views.my_comments, name="comment-me"),
    path("comments/<int:comment_id>/", views.delete_comment, name="comment-delete"),
]
