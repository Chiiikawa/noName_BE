from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserManager(BaseUserManager):
    def create_user(self, password, **fields):
        user = self.model(**fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **fields):
        fields.setdefault("is_admin", True)
        fields.setdefault("is_superuser", True)
        user = self.create_user(**fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        "username",
        max_length=30,
        unique=True,
        validators=[username_validator],
    )
    password = models.CharField("password", max_length=255)
    email = models.EmailField(
        "email",
        max_length=50,
        unique=True,
    )
    profile_image = models.ImageField(
        upload_to="media/userProfile",
        default="media/userProfile/default.png",
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        "phone_number",
        max_length=20,
        unique=True,
    )

    address = models.CharField(
        "adress",
        max_length=100,
        unique=True,
    )
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin


