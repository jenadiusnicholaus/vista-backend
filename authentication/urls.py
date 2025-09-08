

from django.contrib import admin
from django.urls import path, include , re_path 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 
from rest_framework_simplejwt.views import TokenBlacklistView
from . views import (
                    VCheckEmailExistence,
                    VLoginView,
                    VRegisterView,
                    VResendOtpView,
                    VActivateAccountView,
                    ResetPasswordInitView,
                    ResetPasswordConfirmView,
                    PhoneNumberAuthenticationView,
                    VerifyPhoneAndLoginView
                              )
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'user-registration', VRegisterView)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('vlogin/', VLoginView.as_view(), name='custom_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('check-email/', VCheckEmailExistence.as_view(), name='check_email'),
    path('resend-otp/', VResendOtpView.as_view(), name='resend_otp'),
    path('activate-account/', VActivateAccountView.as_view(), name='activate_account'),
    path('get-reset-password-token/', ResetPasswordInitView.as_view(), name='reset_password'),
    path('confirm-reset-password/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('phone-number-auth/', PhoneNumberAuthenticationView.as_view(), name='phone_number_auth'),
    path('verify-phone-number-and-login/', VerifyPhoneAndLoginView.as_view(), name='verify_phone_number_login'),
]
