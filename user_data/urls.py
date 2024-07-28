
from django.contrib import admin
from django.urls import path, include, re_path
from vasta_settings import settings
from .general_views import UserProfileViewSet, MyFavoritePropertyViewsSet,MybookingInforsViewSet, MyBookingBankPaymentDetailsViewSet,MyMobileMoneyPaymentinfosViewSet, MyAddressViewSet,ConfirmBookingViewSet
from .renting_views import MyRentingModelViewSet, ConfirmRentingMWMViewSet
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'user-profile', UserProfileViewSet)
router.register(r'my-favorite-property', MyFavoritePropertyViewsSet)
router.register(r'my-booking-view-set', MybookingInforsViewSet)
router.register(r'my-booking-bank-payment-details', MyBookingBankPaymentDetailsViewSet)
router.register(r'my-mobile-money-payment-infos', MyMobileMoneyPaymentinfosViewSet)
router.register(r'my-address', MyAddressViewSet)
router.register(r'confirm-booking', ConfirmBookingViewSet)
router.register(r'my-renting', MyRentingModelViewSet)
router.register(r'confirm-renting-mwm', ConfirmRentingMWMViewSet)
    





API_VERSION =  settings.API_VERSION

urlpatterns = [
    path('', include(router.urls)), 
   
]
