from pathlib import Path
from datetime import timedelta
import os, json
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = config('OPENAI_API_KEY')

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG')
ALLOWED_HOSTS = [".xn--950b6f504d.store",]

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    # CORS Headers 
    "corsheaders",
    # django 기본 App
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # jwt 인증
    'rest_framework',
    "rest_framework_simplejwt",
    'rest_framework.authtoken',
    # 기타
    'accounts',
    'posts',
    'django.contrib.sites',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'dj_rest_auth',
    'allauth'
]

# Cors, Common: cors-headers 설정
# Authentication: dj-rest-auth 설정
# WhiteNoise, Security: collectstatic을 위한 whitenoise 설정
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",    # 다른 도메인의 fontend에서 backend의 AJAX요청과 같은 크로스 오리진요청을 허용하거나 제한하는데 사용.
    'django.middleware.common.CommonMiddleware',    # 여러 일반적인 작업을 처리함.
    'django.middleware.security.SecurityMiddleware',    # 보안 관련 헤더를 설정하고, 다양한 보안 관련 기능을 제공함.
    'django.contrib.sessions.middleware.SessionMiddleware', # 세션 관리를 위한 미들웨어로, 사용자의 세션을 처리함.
    'django.middleware.csrf.CsrfViewMiddleware',    # CSRF 공격으로부터 보호하기 위해 사용됨. POST 요청에 대한 CSRF 토큰 검사를 함.
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 사용자 인증을 처리함.
    'django.contrib.messages.middleware.MessageMiddleware', # 임시 메세지 저장과 관련된 기능을 제공함. 요청 간에 메세지를 전달할 수 있음.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # 클릭재킹 공격으로부터 보호하기 위해 사용됨.
    'whitenoise.middleware.WhiteNoiseMiddleware',   # django 프로젝트의 정적 파일을 서비스하는데 최적화된 방법을 제공함.
    "allauth.account.middleware.AccountMiddleware",
    "posts.dalle.DALLERateLimitMiddleware", #dalle api 생성 전체 lock
]

# 기본 인증 클래스를 simple-jwt token으로 변경하기 위한 설정.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

ROOT_URLCONF = 'no_name.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'no_name.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr' # Admin 기본 언어 설정

TIME_ZONE = 'Asia/Seoul' # 시간 설정

USE_I18N = True # Django의 번역 시스템 활성화 여부

USE_TZ = True # Django의 시간 인식 활성화 여부


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # django가 collectstatic 명령을 실행할 때 정적 파일을 수집하여 저장할 디렉토리의 경로를 지정함.
 # static_url 은 정적 파일에 접근할 때 사용되는 URL을 설정함. ex) STATIC_URL 이 static/로 설정되어 있으면, 정적 파일들은 http://noname.com/static/와 같은 URL을 통해 접근됨.
STATIC_URL = 'static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# 관리자 유저 모델 설정
AUTH_USER_MODEL = 'accounts.User'

REST_USE_JWT = True

# simplejwt 설정
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=18000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# 모든 URL에 대해 CORS 예외 모두 적용
CORS_ALLOW_ALL_ORIGINS = True
API_REQUEST_POINT = 1

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
