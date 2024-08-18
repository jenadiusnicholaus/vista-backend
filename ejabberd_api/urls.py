
from django.urls import path, include
from vasta_settings import settings
from rest_framework import routers
router = routers.DefaultRouter()

from . views import EjabberdgetRosterView, EjabberdAddRosterItemView
router.register(r'my-rosters', EjabberdgetRosterView)

API_VERSION =  settings.API_VERSION
urlpatterns = [
    path('', include(router.urls)), 
    path(f'add-roster/', EjabberdAddRosterItemView.as_view(), name='add-roster'),
]


