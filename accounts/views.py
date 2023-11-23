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
    
# kakao 소셜로그인
class KakaoLoginView(APIView):
    def post(self, request):
        code = request.data.get('code', None)
        token_url = f'https://kauth.kakao.com/oauth/token'
        redirect_url = config('REDIRECT_URI')
        
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        access_token = request.post(
            token_url,
            data={
                'grant_type': 'authorization_code',
                'client_id': KAKAO_API_KEY,
                'redirect_url': redirect_url,
                'client_secret': KAKAO_SECRET_KEY,
            },
            headers={'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'},
        )
        
        access_token = access_token.json().get('access_token')
        user_data_request = request.get(
            'https://kapi.kakao.com/v2/user/me',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            },
        )
        user_datajson = user_data_request.json()
        user_data = user_datajson.get('kakao_account').get('profile')
        email = user_datajson.get('kakao_account').get('email')
        nickname = user_data.get('nickname'),
        image = user_data.get('thumbnail_image_url', None)
        
        ran_str = ''
        ran_num = random.randint(0, 99999)
        for i in range(10):
            ran_str += str(random.choice(string.ascii_letters + str(ran_num)))
            
        username = 'kakao_' + ran_str
        try:
            user = User.objects.get(email=email)
            type = user.login_type
            if type == 'normal' and user.user_status == 'active':
                return Response(
                    '일반회원으로 이미 가입하셨음. 아이디, 비번을 까먹었다면 아이디 찾기, 비밀번호 재설정을 이용하세요.',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif type != 'kakao':
                return Response(
                    f'{type}으로 가입하셨음. 다시 로그인해주세요.', status=status.HTTP_400_BAD_REQUEST
                )
            elif user.is_active == False:
                return Response(
                    f'{user}님은 탈퇴한 회원.', status=status.HTTP_400_REQUEST
                )
            else:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                refresh["nickname"] = user.nickname
                refresh["login_type"] = user.login_type
                refresh["is_admin"] = user.is_admin
                user.last_login = timezone.now()
                user.save()
                refresh["last_login"] = str(user.last_login)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            user = User.objects.create_user(
                email=email,
                username=username,
                nickname=nickname,
                profileimage=None,
                profileimageurl=image,
                login_type="kakao",
            )
            user.last_login = timezone.now()
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["nickname"] = user.nickname
            refresh["login_type"] = user.login_type
            refresh["is_admin"] = user.is_admin
            refresh["last_login"] = str(user.last_login)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
            