
from django.urls import path, include
from vasta_settings import settings
from rest_framework import routers
from .views import SendFcmNotification, FcmTokenViewSet
router = routers.DefaultRouter()
router.register(r'send-notification', SendFcmNotification, basename='send')  
router.register(r'fcm-token', FcmTokenViewSet, basename='fcm-token')

API_VERSION =  settings.API_VERSION


urlpatterns = [
    path('', include(router.urls)), 
    # path('send-notification/', SendFcmNotification.as_view(), name='send-notification'),

   
]
