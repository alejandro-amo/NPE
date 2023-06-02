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
from django.contrib import admin
from django.urls import path, include
import admin_interface.urls
import admin_api.urls
import authentication.urls
# import old_npe_importer.urls
# admin.autodiscover()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    # Add new routes HERE
    path('', include(admin_api.urls)),

    # Leave admin interface urls as the last line
    path('', include(admin_interface.urls))

]
