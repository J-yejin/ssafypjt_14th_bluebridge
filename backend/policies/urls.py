from django.urls import path
from .views import policy_list, policy_detail

urlpatterns = [
    path('', policy_list),                 # 목록
    path('<int:policy_id>/', policy_detail),  # 상세
]
