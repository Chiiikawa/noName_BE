from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import UserView, LoginView, KakaoView, UserProfileView

urlpatterns = [
    # 로그인
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    # 갱신
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 로그아웃
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # 회원가입
    path("", UserView.as_view(), name="account"),
    # 프로필 조회/수정
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # 카카오톡 결제
    path('kakao-payment-request/', KakaoView.as_view(), name='kakao_payment_request'),
    # 카카오톡 콜백
    path('kakao-payment-approve/', KakaoView.as_view(), name='kakao_payment_approve'),
    ]
