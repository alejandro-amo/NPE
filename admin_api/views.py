from django.shortcuts import render
# Create your views here.
from rest_framework import filters
from .models import Establecimiento
from .serializers import EstablecimientoSerializer
from rest_framework.generics import ListAPIView


class EstablecimientoListView(ListAPIView):
    queryset = Establecimiento.objects.all()
    serializer_class = EstablecimientoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search')
        if search_term:
            queryset = queryset.filter(nombre__icontains=search_term)
        return queryset

