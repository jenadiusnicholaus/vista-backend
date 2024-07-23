from django.urls import path, include
from vasta_settings import settings
from rest_framework import routers
router = routers.DefaultRouter()



API_VERSION =  settings.API_VERSION


urlpatterns = [
    path('', include(router.urls)), 

   
]
