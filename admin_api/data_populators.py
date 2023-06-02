from core import settings
import csv
from .models import TipoEstablecimiento, Poblacion
import logging
logger = logging.getLogger(f'{settings.app_name}.{__name__}')


def populate_poblaciones(apps, schema_editor):
    print()
    logger.info('Checking localities table.')
    if Poblacion.objects.exists():
        logger.info('Localities table seems properly initialized. Leaving as is.')
    else:
        logger.info('Localities table is empty. Putting default values.')
        try:
            # asuming migrations are run fron NPE/npe folder with "python ..\manage.py migrate"
            with open('admin_api/data/municipios.csv', 'r', encoding='utf-8') as csvfile:
                logger.info('CSV file with localities loaded')
                csvreader = csv.reader(csvfile)
                next(csvreader)   # omit headers
                for line in csvreader:
                    try:
                        Poblacion.objects.create(nombre=line[1])
                    except Exception as e:
                        logging.error(f'Exception while populating municipalities database: {e}')
                        exit(1)
        except FileNotFoundError:
            logging.error('Missing localities data. '
                          'Download it from '
                          'https://analisi.transparenciacatalunya.cat/api/views/9aju-tpwc/rows.csv?accessType=DOWNLOAD '
                          'and put it in "admin_api/data" folder.')
            exit(1)


def populate_tipo_establecimiento(apps, schema_editor):
    print()
    logger.info('Checking establishment types table.')
    if TipoEstablecimiento.objects.exists():
        logger.info('Establishment types table seems properly initialized. Leaving as is.')
    else:
        logger.info('Establishment types table is empty. Putting default values.')
        for item in ['Establiments col·laboradors', 'Hospitals i centres de salut', 'Ajuntaments']:
            TipoEstablecimiento.objects.create(nombre=item)
