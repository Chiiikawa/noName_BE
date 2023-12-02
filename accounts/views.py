from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.contrib.auth import get_user_model, authenticate
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import APIView, permission_classes
from accounts.serializers import (
    UserCreateSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from .models import User
from decouple import config
import requests


# 회원가입
class UserView(APIView):
    # 회원가입
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve(조회)를 뜻함. RetrieveUpdateAPIView 는 사용자 프로필의 상세정보를 조회하는 기능을 제공.
# 특정 사용자의 프로필 정보를 가져올 수 있음.
class UserProfileView(generics.RetrieveUpdateAPIView):  
    permission_classes = [permissions.IsAuthenticated]  # 인증된 사용자만 이 뷰에 접근 가능.
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
    
    #프로필 정보 보기는 로그인한 자신만 조회/수정이 가능함.
    def retrieve(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response({"detail": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.get_object() == self.request.user:   # 요청을 보낸 사용자가 인증되었고, 요청이 자신의 프로필을 대상으로 하는지 확인하는 것.
            return super().update(request, *args, **kwargs)
        else:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs): # HTTP PATCH의 요청을 처리함. 리소스의 부분적인 업데이트를 위해 사용됨.
        return self.update(request, *args, **kwargs)