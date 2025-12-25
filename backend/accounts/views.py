from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from .serializers import SignupSerializer, LoginSerializer


@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "signup success"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })


@api_view(['GET'])
def check_username(request):
    username = (request.query_params.get("username") or "").strip()
    if not username:
        return Response({"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
    exists = User.objects.filter(username=username).exists()
    return Response({"available": not exists})
