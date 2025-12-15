from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login), # 로그인
    path('signup/', views.signup), #회원가입
]