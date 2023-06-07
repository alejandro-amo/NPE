"""
URL configuration for npe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    # Establishments datatables view
    re_path(r'establiments/afegir/?$', views.afegir_establiment, name='afegir_establiment'),
    re_path(r'establiments/llistat/?$', views.llistat_establiments, name='llistat_establiments'),
    re_path(r'establiments/detall/?$', views.detall_establiment, name='detall_establiment'),
    re_path(r'^googlemapsproxy/.*$', views.googlemapsproxy, name='googlemapsproxy'),
    re_path(r'^.well-known/.*$', views.well_known, name='well-known'),
    # Establishments datatables view
    # path('detall_establiment', views.detall_establiment, name='detall_establiment'
    # LAST - Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages')
]
