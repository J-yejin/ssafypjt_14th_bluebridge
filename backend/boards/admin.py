from django.contrib import admin

from boards.models import Board, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "user", "views", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "content")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "board", "user", "created_at")
