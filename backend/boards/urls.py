from django.urls import path

from boards import views

urlpatterns = [
    path("", views.board_list, name="board-list"),
    path("<int:pk>/", views.board_detail, name="board-detail"),
    path("<int:pk>/comments/", views.create_comment, name="comment-create"),
    path("comments/<int:comment_id>/", views.delete_comment, name="comment-delete"),
]
