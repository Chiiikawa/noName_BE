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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

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
    #permission_classes=[permissions.AllowAny]
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KakaoView(APIView):
    def kakao_payment_request(self, request):
        # 카카오페이 결제 요청 처리 로직
        url = 'https://kapi.kakao.com/v1/payment/ready'

        headers = {
            'Authorization': 'KAKAO_ADMIN_KEY',  # 실제 카카오페이 Admin Key를 여기에 넣어주세요
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        }

        data = {
            'cid': 'TC0ONETIME',  # 가맹점 CID
            'partner_order_id': 'partner_order_id',  # 가맹점 주문번호
            'partner_user_id': 'partner_user_id',  # 가맹점 회원 ID
            'item_name': '상품명',
            'quantity': 1,
            'total_amount': 10000,  # 결제 금액
            'tax_free_amount': 0,
            'approval_url': 'http://127.0.0.1:3000/success',  # 결제 성공 시 redirect URL
            'cancel_url': 'http://127.0.0.1:3000/cancel',  # 결제 취소 시 redirect URL
            'fail_url': 'http://127.0.0.1:3000/fail',  # 결제 실패 시 redirect URL
        }

        response = requests.post(url, headers=headers, data=data)
        result = response.json()

        return JsonResponse(result)
    
    @csrf_exempt
    def kakao_payment_approve(request):
        if request.method == "POST":
            data = json.loads(request.body.decode("utf-8"))

            # 가맹점에서 저장한 TID와 사용자로부터 전달받은 PG token
            tid = data.get("tid")
            pg_token = data.get("pg_token")

            # 카카오페이 결제 승인 요청 처리 로직
            approve_url = 'https://kapi.kakao.com/v1/payment/approve'

            approve_data = {
                'cid': 'TC0ONETIME',  # 가맹점 CID
                'tid': tid,  # 가맹점에서 저장한 TID
                'partner_order_id': 'partner_order_id',  # 가맹점 주문번호
                'partner_user_id': 'partner_user_id',  # 가맹점 회원 ID
                'pg_token': pg_token,  # 사용자로부터 전달받은 PG token
            }

            approve_response = requests.post(approve_url, headers=headers, data=approve_data)
            approve_result = approve_response.json()

            # 가맹점의 결제 승인 처리 결과에 따른 로직 구현
            return JsonResponse(approve_result)
        return JsonResponse({"message": "잘못된 요청입니다."})