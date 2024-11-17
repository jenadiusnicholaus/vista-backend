"""
Django settings for vasta_settings project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import pymysql

# pymysql.version_info = (1, 4, 6, "final", 0)
pymysql.install_as_MySQLdb()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-177gh)mhx(-h#ei#geenqlet9i(pd9j-a+9cn8#q%0wxzeikah"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "192.168.1.181",
    "127.0.0.1",
    "localhost",
    "192.168.192.42",
    "192.168.1.182",
    "192.168.24.42",
    "192.168.25.42",
    "vista.nexacon.cloud",
]


# Application definition

INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "authentication",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "user_data",
    "host_data",
    "property",
    "fcm",
    "ejabberd_api",
    "corsheaders",
]
X_FRAME_OPTIONS = "SAMEORIGIN"  # allows you to use modals insated of popups
SILENCED_SYSTEM_CHECKS = ["security.W019"]  # allows you to use modals insated of popups

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vasta_settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "vasta_settings.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     #  "default": {
#     #     "ENGINE": "django.db.backends.postgresql",
#     #     "NAME":config('DB_NAME', default='db_name'),
#     #     "USER":config('DB_USER', default='db_user'),
#     #     "PASSWORD":config('DB_PASSWORD', default='db_password'),
#     # }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DATABASE_NAME"),
        "USER": config("DATABASE_USER"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": config("DATABASE_HOST"),
        "PORT": config("DATABASE_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Or another default permission
    ],
}

AUTHENTICATION_BACKENDS = (
    # Django
    "django.contrib.auth.backends.ModelBackend",
)


# Google configuration
GOOGLE_CLIENT_ID = (
    "136464011660-r1c7mri92r9jsvb4da89qc18qa4lng5m.apps.googleusercontent.com"
)


SITE_ID = 1


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"
# // tanzania time zone
TIME_ZONE = "Africa/Dar_es_Salaam"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "static/"
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
MADIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

API_VERSION = "v1"

AUTH_USER_MODEL = "authentication.CustomUser"


# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="no_email")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="no_password")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# AZAM PAY
AZAM_PAY_AUTH = config("AZAM_PAY_AUTH", default="no_auth")
AZAM_PAY_CHECKOUT_URL = config("AZAM_PAY_CHECKOUT_URL", default="no_checkout_url")
AZAM_PAY_APP_NAME = config("AZAM_PAY_APP_NAME", default="no_app_name")
AZAM_PAY_CLIENT_ID = config("AZAM_PAY_CLIENT_ID", default="no_client_id")
AZAM_PAY_CLIENT_SECRET = config("AZAM_PAY_CLIENT_SECRET", default="no_client_secret")
TOKEN = config("TOKEN", default="no_token")

EJABBERD_API_BU = config("EJABBERD_API_BU", default="no_ejabberd_api_url")
EJABBERD_API_ACCESS_TOKEN = config(
    "EJABBERD_API_ACCESS_TOKEN", default="no_ejabberd_api_access_token"
)

# cors headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://192.168.1.181",
    "http://192.168.1.182",
    "http://192.168.24.42",
    "http://192.168.25.42",
    "http://vista.nexacon.cloud",
    "https://127.0.0.1",
    "https://vista.nexacon.cloud",
]

CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False
