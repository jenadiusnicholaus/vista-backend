
from django.urls import path, include
from vasta_settings import settings
from rest_framework import routers
router = routers.DefaultRouter()

from .views import GetPropertysPaginationView, GetPropertyDetailsViewSet
router.register(r'property-list', GetPropertysPaginationView)
router.register(r'property-details', GetPropertyDetailsViewSet, basename='property-details')


API_VERSION =  settings.API_VERSION


urlpatterns = [
    path('', include(router.urls)), 

   
]
