from .models import Establecimiento, TipoEstablecimiento
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EstablecimientoSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


class EstablishmentPagination(PageNumberPagination):
    page_size = 100
    page_query_param = 'pagina'
    page_size_query_param = 'porpag'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def establecimiento_api_view(request):
    if request.method == 'GET':
        paginator = EstablishmentPagination()
        # sort by column
        sort_by = request.query_params.get('ordenar_por')
        if not sort_by or sort_by not in ['id', 'nombre', 'direccion', 'poblacion', 'codigo_postal', 'fecha_creacion',
                                          'fecha_actualizacion', 'activo']:
            sort_by = 'id'
        # reverse order yes/no (sorty by X desc)
        reverse_order = request.query_params.get('orden_inverso')
        if reverse_order and reverse_order in ['1', 'true', 't', 'verdadero', 'v']:
            sort_by = f'-{sort_by}'  # i.e. "ciudad" becomes "-ciudad". that's how reverse order is expressed ;)
        # search term
        searchterm = request.query_params.get('buscar')
        if searchterm:
            establecimientos = Establecimiento.objects.filter(
                Q(nombre__icontains=searchterm) |
                Q(direccion__icontains=searchterm) |
                Q(codigo_postal__icontains=searchterm) |
                Q(poblacion__icontains=searchterm)
            ).order_by(sort_by)
        else:
            establecimientos = Establecimiento.objects.all().order_by('-id')
        include_disabled = request.query_params.get('incluir_inactivos')
        if include_disabled and include_disabled in ['1', 'true', 't', 'verdadero', 'v']:
            pass  # include disabled establishments, so nothing to filter out
        else:
            establecimientos = establecimientos.filter(activo=1)
        page = paginator.paginate_queryset(establecimientos, request)
        establecimientos_serializer = EstablecimientoSerializer(page, many=True)
        return paginator.get_paginated_response(establecimientos_serializer.data)

    if request.method == 'POST':
        # request is needed to be provided because we use usernames for creation/update traceability
        establecimiento_serializer = EstablecimientoSerializer(data=request.data, context={'request': request})
        if establecimiento_serializer.is_valid():
            establecimiento_serializer.save()
            return Response(establecimiento_serializer.data, status=status.HTTP_201_CREATED)
        return Response(establecimiento_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def single_establecimiento_api_view(request, pk=None):
    establecimiento = Establecimiento.objects.filter(id=pk).first()
    if establecimiento:
        if request.method == 'GET':
            establecimiento_serializer = EstablecimientoSerializer(establecimiento)
            return Response(establecimiento_serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            # request is needed to be provided because we use usernames for creation/update traceability
            establecimiento_serializer = EstablecimientoSerializer(establecimiento, data=request.data,
                                                                   context={'request': request})
            if establecimiento_serializer.is_valid():
                establecimiento_serializer.save()
                return Response(establecimiento_serializer.data, status=status.HTTP_200_OK)
            return Response(establecimiento_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'No se encuentra el establecimiento con el ID especificado'},
                    status=status.HTTP_404_NOT_FOUND)


class EstablecimientoViewSet(viewsets.ModelViewSet):
    queryset = Establecimiento.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EstablecimientoSerializer


class EstablecimientoApiView(APIView):

    def get(self, request):
        establecimientos = Establecimiento.objects.all()
        establecimientos_serializer = EstablecimientoSerializer(Establecimiento, many=True)
        return Response(establecimientos_serializer.data)
