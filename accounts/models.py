from django.db import models    # models을 사용할거다~
from django.contrib.auth.models import (
    BaseUserManager,    # Django의 기본 UserManager를 상속받아 custom해서 사용
    AbstractBaseUser,   # Django의 기본 Usermodel을 상속받아 custom해서 사용
    PermissionsMixin,
)
# django의 사용자 인증 시스템에서 사용자 이름의 유효성을 검사하기 위해 UnicodeUsernameValidator 클래스를 가져오는 것.
from django.contrib.auth.validators import UnicodeUsernameValidator 


class UserManager(BaseUserManager): # BaseUserManager 상속받아 custom
    def create_user(self, password, **fields): # BaseUserManager의 create_user method를 overiding한다.
        user = self.model(**fields) # user라는 변수에 객체의 모델에 모든 인자(field)를 다 넣어서 전달
        user.set_password(password) # 기본적으로 제공되는 set_password라는 함수를 사용해 user 변수에 있는 password를 암호화 
        # 생성된 사용자 객체('user')를 데이터베이스에 저장. 
        # 'using=self._db' 사용할 데이터베이스를 명시하는데, 
        # 여러 데이터베이스를 사용하는 경우 중 어떤 데이터베이스를 사용할지 지정하는 것
        user.save(using=self._db)   
        return user

    def create_superuser(self, **fields):   # BaseUserManager의 create_superuser method를 overiding을 한다.
        fields.setdefault("is_admin", True) # 'fields' 딕셔너리에 'is_admin' 키가 없을 경우, 기본값으로 'True'를 설정한다. 즉. 생성되는 슈퍼유저는 기본적으로 관지라 권한을 가진다.
        fields.setdefault("is_superuser", True) # 'is_superuser'키가 'fields' 딕셔너리에 없으면, 이를 'True'로 설정한다. 생성되는 사용자가 슈퍼유저임을 의미한다.
        fields.setdefault("is_active", True)    # 'is_activate'키에 대해 'fields' 딕녀서리에 기본값으로 'True'를 설정한다. 슈퍼유저 계정이 활성화된 상태를 의미한다.
        user = self.create_user(**fields)   # 'create_user' 메서드를 사용하여 새로운 사용자를 생성한다. 여기서 '**fields'는 이전에 설정한 관리자, 슈퍼유저, 활성화 상태 등을 포함한 모든 필드를 'creaute_user' 메서드에 전달한다.
        user.save(using=self._db)   # 생성된 사용자 객체('user')를 데이터베이스에 저장한다. 'using=self._db' 사용할 데이터베이스를 명시하는데, 여러 데이터베이스를 사용하는 경우 중 어떤 데이터베이스를 사용할지 지정하는 것.
        return user # 생성되고 저장된 사용자 객체를 반환하는것.


class User(AbstractBaseUser, PermissionsMixin): # import한 AbstractBaseUser에 PermissionsMixin을 다중상속
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        "username", # verbose_name을 username으로 지정
        max_length=30,  # Charfield에서는 max_length를 꼭 설정해줘야함.
        unique=True,    # username은 u하
        validators=[username_validator],
    )
    password = models.CharField("password", max_length=255) # 사용자의 비밀번호를 저장하는 필드 입니다. 최대 길이는 255.
    email = models.EmailField(
        "email",
        max_length=50,
        unique=True,
    )   # 사용자의 이메일을 저장하는 필드. 최대 길이는 50자이며, 이메일은 고유해야 한다.
    profile_image = models.ImageField(
        upload_to="profile-image",
        blank=True,
        null=True,
    )   # 사용자의 프로필 이미지를 저장하는 필드. 이미지는 'media/userProfile' 디렉토리에 저장되며, 기본값으로 'media/userPProfile/default.png'가 설정된다. 이필드는 선택 사항입니다.
    phone_number = models.CharField(
        "phone_number",
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )   # 사용자의 전화번호를 저장하는 필드. 최대 길이는 20이며, 전화번호는 고유해야 한다. 이 필드 역시 선택사항

    nickname = models.CharField(
        "nickname",
        max_length=10,
        blank=True,
        null=True,
    )

    address = models.CharField(
        "address",
        max_length=100,
        blank=True,
        null=True,
    )
    
    zipcode = models.CharField(
        'zipcode',
        max_length=100,
        blank=True,
        null=True,
    )
    LOGIN_TYPE = [
        ("normal", "일반"),
        ("kakao", "카카오"),
    ]
    login_type = models.CharField(
        "로그인 타입", max_length=10, choices=LOGIN_TYPE, default="normal", null=True
    )


    
    is_active = models.BooleanField(default=True)   # 사용자의 활성화 상태를 나타내는 필드
    is_admin = models.BooleanField(default=False)   # 사용자가 관리자인지 여부를 나타내는 필드
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager() # 사용자 모델에 대한 사용자 관리자('UserManager')인스턴스를 할당한다. 이는 사용자 생성 및 관리와 관련된 추가 메서드를 제공함.

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

