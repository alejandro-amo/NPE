import os.path

from django.core.management.base import BaseCommand
from geojson import Feature, Point, FeatureCollection, dumps
from json import loads
from admin_api.models import Establecimiento
import logging
from django.db.models import Q
from core import settings
logger = logging.getLogger(f'{settings.app_name}.{__name__}')


class Command(BaseCommand):
    help = "Builds the GEOJSON data that is used in frontend of NPE App. " \
           "It's stored in database and retrieved by NPE App using /api/geojsondata endpoint"

    def handle(self, *args, **options):
        logger.debug('Querying database for active establishments')
        active_establishments_queryset = Establecimiento.objects.filter(activo=True)
        # also filter establishments with (0,0) which is how we mark them as "GPS Coords not calculated"
        active_and_nonzerocoords_establishments_queryset = active_establishments_queryset.exclude(Q(latitud=0) |
                                                                                                  Q(longitud=0))
        establishments_amount = active_and_nonzerocoords_establishments_queryset.count()
        logger.info(f'GEOJSON file will be generated with data from {establishments_amount} establishments.')
        lista_geojson_features = []
        for establishment in active_establishments_queryset:
            establishment_id = establishment.id
            logger.debug(f'Processing data from ID {establishment_id}...')
            latitud = float(establishment.latitud)
            longitud = float(establishment.longitud)
            if latitud == 0 and longitud == 0:
                continue
            nombre = establishment.nombre
            direccion = establishment.direccion
            poblacion = establishment.poblacion
            telefono = establishment.telefonos
            codigopostal = establishment.codigo_postal
            propiedades = {
                'nombre': nombre,
                'direccion': direccion,
                'poblacion': poblacion,
                'telefono': telefono,
                'codigopostal': codigopostal
            }
            point = Point((longitud, latitud))
            feature = Feature(geometry=point, properties=propiedades)
            lista_geojson_features.append(feature)
        feature_collection = FeatureCollection(lista_geojson_features)
        # store geojson data file
        geojsondata = dumps(loads(dumps(feature_collection)), indent=4, sort_keys=False)
        outputfilename = os.path.join(settings.CORE_DIR, 'admin_api', 'data', 'npedata.geojson')
        with open(outputfilename, 'w', encoding='utf-8') as file:
            file.write(geojsondata)
        logger.info(f'GEOJSON data (re)generated and stored in {outputfilename} successfully.')
