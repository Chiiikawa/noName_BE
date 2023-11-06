from rest_framework import serializers
from accounts.models import User, History
from django.contrib.auth import get_user_model


class UserCreateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "password",
            "nickname",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    history_logs = serializers.SerializerMethodField()

    def get_history_logs(self, obj):
        logs = History.objects.filter(user=obj).order_by("-created_at")
        return [
            {"created_at": log.created_at, "action": log.action, "point": log.point}
            for log in logs
        ]

    class Meta:
        model = User
        fields = ["email", "point", "nickname", "history_logs"]



