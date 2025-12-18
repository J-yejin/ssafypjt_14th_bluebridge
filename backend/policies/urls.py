from django.urls import path
from policies import views

urlpatterns = [
    path("", views.policy_list, name="policy-list"),
    path("<int:id>/", views.policy_detail, name="policy-detail"),
]
