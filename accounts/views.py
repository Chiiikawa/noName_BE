from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from rest_framework.generics import get_object_or_404
from accounts.serializers import (
    UserCreateSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from .models import User
from rest_framework import status,permissions
from rest_framework.decorators import APIView, permission_classes
from rest_framework.permissions import AllowAny

# create your views here.
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
            
    def put(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserCreateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    #프로필 정보 보기    
    def get(self, request, user_id=None):
       if user_id:
           target = get_object_or_404(get_user_model(), pk=user_id)
       else:
           if not request.user.is_authenticated:
               return Response(
                   {"detail": "로그인 해주세요."}, status=status.HTTP_401_UNAUTHORIZED
               )
       serializer = UserProfileSerializer(target)
       return Response(serializer.data, status=status.HTTP_200_OK)
   
class LoginView(TokenObtainPairView):
    permission_classes=[permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
