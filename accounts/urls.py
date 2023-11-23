from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from .views import UserView, LoginView, UserProfileView, KakaoLoginView

urlpatterns = ([
    # kakao 로그인
    path("kakao-login/", views.KakaoLoginView.as_view(), name="kakao_login"),
    # 로그인
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    # 갱신
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 회원가입
    path("", UserView.as_view(), name="account"),
    # 프로필 조회/수정
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
)