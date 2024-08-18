
from django.urls import path, include
from vasta_settings import settings
from rest_framework import routers
router = routers.DefaultRouter()

from .views import GetPropertysPaginationView, GetPropertyDetailsViewSet, GetCategoriesView, ReviewThePropertyView,SupportedGeoRegionsViewSet
router.register(r'property-list', GetPropertysPaginationView)
router.register(r'property-details', GetPropertyDetailsViewSet, basename='property-details')
router.register(r'categories', GetCategoriesView)
router.register(r'review-property', ReviewThePropertyView)
router.register(r'supported-geo-regions', SupportedGeoRegionsViewSet)

API_VERSION =  settings.API_VERSION


urlpatterns = [
    path('', include(router.urls)), 

   
]
