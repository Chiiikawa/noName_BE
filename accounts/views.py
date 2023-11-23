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
class KakaoLogin(APIView):
    def post(self, request):
        
        state = config("STATE") # 환경 변수에서 STATE라는 이름의 값을 가져와 state변수에 저장, OAuth 인증 과정에서 사용될수 있음.
        client_id = config('KAKAO_API_KEY')
        
        received_code = request.data.get('code')    # 이 코드는 Kakao로부터 받은 인증코드
        print("received_code:", received_code)
        code_value = received_code.split('?code=')[-1]  # ?code= 를 기준으로 문자열을 분리, 마지막 부분을 code_value로 저장, URL에서 인증코드만 추출하는 과정.
        print(code_value)
        
        
        kakao_token = requests.post(
            'https://kauth.kakao.com/ouath/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'redirect_url': 'http://localhost:3000/oauth/callback/kakao',
                'code': code_value
            },
        )
        print(kakao_token.json()['access_token'])   # 받은 응답에서 JSON형태로 변환한 뒤, access_token을 추출하여 출력함.
        access_token = kakao_token.json()['access_token']
        refresh_token = kakao_token.json()['refresh_token']
        
        token_data = {'access': access_token, 'refresh': refresh_token} # access, refresh 토큰을 token_data 딕셔너리에 저장.
        
        # access_token 으로 사용자 정보 가져오기
        user_data = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers={'Authorization' : f'Bearer {access_token}'},
        )
        # 이메일, 프로필 사진 가져오기
        user_data = user_data.json()
        
        kakao_account = user_data.get('kakao_account')
        user_email = kakao_account.get('email')
        user_nickname = kakao_account.get('profile')['nickname']
        user_img = kakao_account.get('profile')['profile_image_url']
        
        # 데이터베이스에서 사용자를 조회하고, 존재하지 않는 경우 새로운 사용자를 생성하는 로직을 포함하는 try-except 블록
        try:
            user = User.objects.get(email=user_email)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            print(user.nickname, user.email, 'password', user.password)
            
            token_data['user_profile'] = {'uid' : user.id, 'email': user.email}
            return Response(data=token_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:   # User.DoesNotExist 는 예외를 처리하는 블록. 사용자가 데이터베이스에 없으면 새로운 사용자를 생성, 로그인 처리 후 응답을 반환함.
            user = User.objects.create(
                email=user_email,
                nickname=user_nickname,
                profile_img=user_img,
            )
            user.set_unusable_password()
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            print(user.nickname, user.email, 'password', user.password)
            
            token_data['user_profiel'] = {'uid' : user.id, 'email' : user.email}
            return Response(data=token_data, status=status.HTTP_200_OK)
        except Exception:   # 기다 예외를 처리하는 블록. 400HTTP 상태코드를 반환하는 응답을 생성
            return Response(status=status.HTTP_400_BAD_REQUEST)