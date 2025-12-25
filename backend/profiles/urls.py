from django.urls import path
from .views import my_profile, user_profile

urlpatterns = [
    path('me/', my_profile),
    path('<str:username>/', user_profile),
]
