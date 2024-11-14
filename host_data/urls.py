from django.urls import path, include
from vasta_settings import settings
from rest_framework import routers
from .views import( 
    HostPropertysPaginationView,
    PropertyRulesViewSet,
    PropertyImagesViewSet,
    PropertyFacilitiesViewSet,
    PropertyAmenitiesViewSet
    )
router = routers.DefaultRouter()
router.register(r'host-property-view-set', HostPropertysPaginationView, basename='host_data')
router.register(r'host-property-rules-view-set', PropertyRulesViewSet)
router.register(r'host-property-images-view-set', PropertyImagesViewSet)
router.register(r'host-property-facilities-view-set', PropertyFacilitiesViewSet)
router.register(r'host-property-amenities-view-set', PropertyAmenitiesViewSet)

API_VERSION =  settings.API_VERSION


urlpatterns = [
    path('', include(router.urls)),
]
