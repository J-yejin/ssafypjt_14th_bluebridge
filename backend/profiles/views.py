from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Profile
from .serializers import ProfileSerializer


# 자기 자신 프로필 조회, 수정
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

# 남의 프로필 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)