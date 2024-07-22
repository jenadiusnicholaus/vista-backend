
from django.contrib import admin
from django.urls import path, include, re_path
from vasta_settings import settings
from .views import UserProfileViewSet, MyFavoritePropertyViewsSet
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'user-profile', UserProfileViewSet)
router.register(r'my-favorite-property', MyFavoritePropertyViewsSet)


API_VERSION =  settings.API_VERSION

urlpatterns = [
    path('', include(router.urls)), 
   
]
