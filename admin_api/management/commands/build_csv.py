import csv
import os.path
from django.core.management.base import BaseCommand
from admin_api.models import Establecimiento
import logging
from django.db.models import Q
from core import settings

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


class Command(BaseCommand):
    help = "Builds a CSV file with establishment data."

    def handle(self, *args, **options):
        logger.debug('Querying database for active establishments')
        active_establishments_queryset = Establecimiento.objects.filter(activo=True)
        active_and_nonzerocoords_establishments_queryset = active_establishments_queryset.exclude(Q(latitud=0) |
                                                                                                  Q(longitud=0))
        establishments_amount = active_and_nonzerocoords_establishments_queryset.count()
        logger.info(f'CSV file will be generated with data from {establishments_amount} establishments.')

        # Define the filename for the CSV output
        outputfilename = os.path.join(settings.CORE_DIR, 'admin_api', 'data', 'npedata.csv')

        with open(outputfilename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'tipus', 'nom', 'direccio', 'municipi', 'telefons', 'codipostal', 'latitud', 'longitud', 'web', 'approved']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

            writer.writeheader()
            for establishment in active_establishments_queryset:
                if establishment.latitud == 0 and establishment.longitud == 0:
                    continue
                writer.writerow({
                    'id': establishment.id,
                    'tipus': establishment.tipo_establecimiento,
                    'nom': establishment.nombre,
                    'direccio': establishment.direccion,
                    'municipi': establishment.poblacion,
                    'telefons': establishment.telefonos,
                    'codipostal': establishment.codigo_postal,
                    'latitud': establishment.latitud,
                    'longitud': establishment.longitud,
                    'web': establishment.web,
                    'approved': 1
                })

        logger.info(f'CSV data (re)generated and stored in {outputfilename} successfully.')
