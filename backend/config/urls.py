from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bluebridge/auth/', include('accounts.urls')),
    path('bluebridge/profile/', include('profiles.urls')),
    path('bluebridge/policies/', include('policies.urls')),
    path('bluebridge/boards/', include('boards.urls')),
    path('bluebridge/wishlist/', include('policies.wishlist_urls')),
]
