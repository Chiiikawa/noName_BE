from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User
from django.contrib.auth import get_user_model


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "password",
            "profile_image",
            "phone_number",
            "nickname",
            "address",
            'zipcode',
        )
        
    def create(self, validated_data):
        password = validated_data.pop("password")   # 유효한 데이터로부터 'password'를 추출하고, 데이터에서 제거한다.
        user = User(**validated_data)
        user.set_password(password) # 사용자 객체에 비밀번호를 설정, 'set_password' 메서드는 비밀번호를 해시 처리 함.
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod    # 아래의 메서드를 클래스 메서드로 정의한다. 클래스 메서드는 인스턴스가 아닌 클래스 자체에 속함.
    def get_token(cls, user):
        token = super().get_token(user) # 기본 토큰을 생성
        token['email'] = user.email
        return token
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "profile_image",
            "phone_number",
            "nickname",
            "address",
            "zipcode",
            "point",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "username", "email", "point", "created_at") # 읽기 전용 필드. 이 필드들은 수정 불가능.
    
    def update(self, instance, validated_data):
        # Only update the fields that can be modified by the user
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.address = validated_data.get('address', instance.address)
        instance.zipcode = validated_data.get('zipcode', instance.zipcode)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)

        # Save and return the updated instance
        instance.save()
        return instance