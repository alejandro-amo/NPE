from django.urls import path
from .api import establecimiento_api_view, single_establecimiento_api_view
urlpatterns = [
    path('api/establecimientos/', establecimiento_api_view, name='establecimientos_api'),
    path('api/establecimientos/<int:pk>/', single_establecimiento_api_view, name='single_establecimiento_api')
]
