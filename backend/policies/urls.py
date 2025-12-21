from django.urls import path
from policies import views

urlpatterns = [
    path("", views.policy_list, name="policy-list"),
    path("<int:id>/", views.policy_detail, name="policy-detail"),
    path("search/", views.policy_search, name="policy-search"),
    path("wishlist/", views.wishlist_list_create, name="wishlist-list-create"),
    path("wishlist/<int:policy_id>/", views.wishlist_delete, name="wishlist-delete"),
]
