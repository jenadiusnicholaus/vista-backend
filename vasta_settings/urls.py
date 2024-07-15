"""vasta_settings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from vasta_settings import settings

API_VERSION =  settings.API_VERSION

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')) ,
    path(f"api/{API_VERSION}/authentication/", include("authentication.urls")), 
    re_path(r'^api/v1/social/', include('drf_social_oauth2.urls', namespace='drf')),
    path(f"api/{API_VERSION}/user-data/", include("user_data.urls")),


]
