from django.core.management.base import BaseCommand
from admin_api.models import Establecimiento, Poblacion
import logging
from core import settings
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from unidecode import unidecode

logger = logging.getLogger(f'{settings.app_name}.{__name__}')

establecimientos = Establecimiento.objects.all()
lista_poblaciones = [p.nombre for p in Poblacion.objects.all()]
lista_poblaciones_relaxed = [unidecode(p.lower()) for p in lista_poblaciones]


def recover_case(whatcity):
    for this_city in lista_poblaciones:
        if unidecode(this_city.lower()) == whatcity:
            # it should ALWAYS happen because we arrive here from a coincidence
            return this_city
    print('We should never get here!')
    raise KeyError  # it should NEVER happen


class Command(BaseCommand):
    help = "Builds the GEOJSON data that is used in frontend of NPE App. " \
           "It's stored in database and retrieved by NPE App using /api/geojsondata endpoint"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        logger.debug('Querying database for city/town of each establishment')

        fixed = 0
        needfixing = 0
        with open('fuzzy_matching.txt', 'w', encoding='utf-8') as resultsfile:
            for establecimiento in establecimientos:
                est_id = establecimiento.id
                poblacion = establecimiento.poblacion
                poblacion = poblacion.strip()
                poblacion = poblacion.lower()
                poblacion = unidecode(poblacion)
                if poblacion.startswith('l\''):
                    poblacion = poblacion[2:] + ', l\''
                if poblacion.startswith('els '):
                    poblacion = poblacion[4:] + ', els'
                if poblacion.startswith('el '):
                    poblacion = poblacion[3:] + ', el'
                if poblacion.startswith('la '):
                    poblacion = poblacion[3:] + ', la'
                if poblacion.startswith('les '):
                    poblacion = poblacion[4:] + ', les'
                coincidencia = process.extractOne(poblacion, lista_poblaciones_relaxed)[0]
                ratio = fuzz.ratio(poblacion, coincidencia)
                coincidencia = recover_case(coincidencia)
                line = f'ID:{est_id} | "{poblacion}"\t\t=> {coincidencia} (Ratio: {ratio}%)'
                if ratio < 100:
                    logger.info(line)
                    resultsfile.write(f'{line}')
                    needfixing += 1
                else:
                    '''
                    establecimiento.poblacion = poblacion
                    establecimiento.save()
                    '''
                    updating_establecimiento = Establecimiento.objects.get(id=est_id)
                    # old_poblacion = updating_establecimiento.poblacion
                    # logger.info(f'Updating database entry {est_id} "{old_poblacion}" to "{coincidencia}"')
                    updating_establecimiento.poblacion = coincidencia
                    updating_establecimiento.save()
                    fixed += 1

        logger.info(f'Finished. {fixed} establishments are now in sync with the closed list of options. '
                    f'{needfixing} still need fixing.')
