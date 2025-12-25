from django.urls import path

from . import views

urlpatterns = [
    path("", views.recommend_list, name="recommend-list"),
    path("detail/", views.recommend_detail, name="recommend-detail"),
]
