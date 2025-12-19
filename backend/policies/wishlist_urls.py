from django.urls import path
from policies import views

urlpatterns = [
    path("", views.wishlist_list_create, name="wishlist-list-create"),
    path("<int:policy_id>/", views.wishlist_delete, name="wishlist-delete"),
]
