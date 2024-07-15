
from django.contrib import admin
from django.urls import path, include, re_path
from vasta_settings import settings
from .views import UserProfileViewSet
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'user-profile', UserProfileViewSet)

API_VERSION =  settings.API_VERSION

urlpatterns = [
    path('', include(router.urls)), 
   
]
