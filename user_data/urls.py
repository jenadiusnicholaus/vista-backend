
from django.contrib import admin
from django.urls import path, include, re_path
from user_data.booking_views import ConfirmBookingViewSet, MyBankPaymentDetailsViewSet, MybookingInforsViewSet,BookingRequestViewSet
from user_data.azam_pay_webhooks import AzamPayWebhookView, PaymentStatusCheckView
from vasta_settings import settings
from .global_views import UserProfileViewSet, MyFavoritePropertyViewsSet,MyMobileMoneyPaymentinfosViewSet, MyAddressViewSet
from .renting_views import MyRentingModelViewSet, ConfirmRentingMWMViewSet, MyRentingRequestViewSet 
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'user-profile', UserProfileViewSet)
router.register(r'my-favorite-property', MyFavoritePropertyViewsSet)
router.register(r'my-booking-view-set', MybookingInforsViewSet)
router.register(r'my-booking-bank-payment-details', MyBankPaymentDetailsViewSet)
router.register(r'my-mobile-money-payment-infos', MyMobileMoneyPaymentinfosViewSet)
router.register(r'my-address', MyAddressViewSet)
router.register(r'confirm-booking', ConfirmBookingViewSet)
router.register(r'my-renting', MyRentingModelViewSet)
router.register(r'confirm-renting-mwm', ConfirmRentingMWMViewSet)
router.register(r'my-booking-request', BookingRequestViewSet, basename='my-booking-request')
router.register(r'my-renting-request', MyRentingRequestViewSet, basename='my-renting-request')
    
API_VERSION =  settings.API_VERSION

urlpatterns = [
    path('', include(router.urls)),
    path('azam-pay/webhook/', AzamPayWebhookView.as_view(), name='azam-pay-webhook'),
    path('azam-pay/status-check/', PaymentStatusCheckView.as_view(), name='azam-pay-status-check'),
]
