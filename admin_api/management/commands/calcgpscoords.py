from django.utils import timezone
from django.core.management.base import BaseCommand
import json
import requests
from urllib.parse import urlencode
from core import settings
from admin_api.models import Establecimiento, MetadatosEstablecimiento
import logging

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


def actualizar_coordenadas_desde_google(id_establecimiento):
    try:
        data = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first().google_result
        google_data = json.loads(data)
        # logger.debug(f'Google Places data stored: {data}')
        if google_data['status'] == 'ZERO_RESULTS':
            logger.info(f'Google Places API answer for establishment with id {id_establecimiento} was empty. '
                        f'Returning None for GPS coords.')
            return None

    except Exception as e:
        logger.error(f'Exception while retrieving Google Places data for establishment {id_establecimiento}: {e}')
        return False
    try:
        latitud = float(google_data['results'][0]['geometry']['location']['lat'])
        longitud = float(google_data['results'][0]['geometry']['location']['lng'])
        logger.debug(f'Parsed GPS coords: {latitud},{longitud}')
    except (KeyError, IndexError) as e:
        logger.error(f'While parsing stored data from Google places API (GPS coords for id={id_establecimiento}): {e}')
        return False
    try:
        establecimiento_a_actualizar = Establecimiento.objects.filter(id=id_establecimiento).first()
        establecimiento_a_actualizar.latitud = latitud
        establecimiento_a_actualizar.longitud = longitud
        establecimiento_a_actualizar.actualizado_por = 'Calculador de coordenadas GPS'
        establecimiento_a_actualizar.fecha_actualizacion = timezone.now()
        establecimiento_a_actualizar.save()
        return True
    except Exception as e:
        logger.error(f'While storing new GPS coords for establishment {id_establecimiento}: {e}')
        return False


def actualizar_coordenadas_desde_nominatim(id_establecimiento):
    try:
        data = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first().nominatim_result
        if data == '[]':
            logger.info(
                f'Nominatim answer for establishment with id {id_establecimiento} was empty. '
                f'Returning None for GPS coords.')
            return None
        nominatim_data = json.loads(data)
    except Exception as e:
        logger.error(f'Exception while retrieving nominatim data for establishment {id_establecimiento}: {e}')
        return False
    try:
        latitud = float(nominatim_data[0]['lat'])
        longitud = float(nominatim_data[0]['lon'])
        logger.debug(f'Parsed GPS coords: {latitud},{longitud}')
    except (KeyError, IndexError) as e:
        logger.error(f'While parsing stored data from Nominatim API (GPS coords for id={id_establecimiento}): {e}')
        return False
    try:
        establecimiento_a_actualizar = Establecimiento.objects.filter(id=id_establecimiento).first()
        establecimiento_a_actualizar.latitud = latitud
        establecimiento_a_actualizar.longitud = longitud
        establecimiento_a_actualizar.actualizado_por = 'Calculador de coordenadas GPS'
        establecimiento_a_actualizar.fecha_actualizacion = timezone.now()
        establecimiento_a_actualizar.save()
        return True
    except Exception as e:
        logger.error(f'While storing new GPS coords for establishment {id_establecimiento}: {e}')
        return False


def actualizar_cp_desde_nominatim(id_establecimiento):
    try:
        data = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first().nominatim_result
        if data == '[]':
            logger.info(
                f'Nominatim answer for establishment with id {id_establecimiento} was empty. '
                f'Returning None for postal code.')
            return None
        nominatim_data = json.loads(data)
    except Exception as e:
        logger.error(f'Exception while retrieving nominatim data for establishment {id_establecimiento}: {e}')
        return False
    try:
        cp = nominatim_data[0]['address']['postcode']
        logger.debug(f'Parsed postal code: {cp}')
    except (KeyError, IndexError) as e:
        logger.error(f'While parsing stored data from Nominatim API (postal code for id={id_establecimiento}): {e}')
        return False
    try:
        establecimiento_a_actualizar = Establecimiento.objects.filter(id=id_establecimiento).first()
        establecimiento_a_actualizar.codigo_postal = cp
        establecimiento_a_actualizar.actualizado_por = 'Calculador de códigos postales'
        establecimiento_a_actualizar.fecha_actualizacion = timezone.now()
        establecimiento_a_actualizar.save()
        return True
    except Exception as e:
        logger.error(f'While storing new postal code coords for establishment {id_establecimiento}: {e}')
        return False


def obtener_google_id_establecimiento(id_establecimiento, nocache=False):
    establecimiento = Establecimiento.objects.filter(id=id_establecimiento).first()
    if not establecimiento:
        logger.error(f'Obtaining Nominatim data: no establishment found with id {id_establecimiento}. Omitting.')
        return {}
    else:
        metadatos_establecimiento = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first()
        if metadatos_establecimiento.google_checked:
            # nocache ignores cached content and queries API again, no matter what
            if metadatos_establecimiento and not nocache:
                if metadatos_establecimiento.google_checked > establecimiento.fecha_actualizacion:
                    logger.info(f'Using cached Google maps results for establishment with id {id_establecimiento}.')
                    cached = True
                    return metadatos_establecimiento.google_result, cached
        nombre = establecimiento.nombre
        direccion = establecimiento.direccion
        # codigo_postal = establecimiento.codigo_postal
        poblacion = establecimiento.poblacion
        '''
        logger.debug(f'Obtaining Google maps data. Will use the following data from establishment {id_establecimiento}:'
                             f'locality={poblacion}, address={direccion}')
        '''
        # google_bias = '40.522,0.158|42.868,3.327'  # Prioritize results in Catalonia
        # Create the request URL with the provided parameters
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?language=ca&query=" \
              f"{nombre}+{direccion}+{poblacion}&key={settings.GOOGLE_API_KEY}"

        try:
            # Send a GET request to the Geocoding API
            response = requests.get(url)
            response.encoding = 'utf-8'
            data = response.text
            jsondata = json.loads(data)

            if response.status_code == 200 and (jsondata['status'] == 'OK' or jsondata['status'] == 'ZERO_RESULTS'):
                cached = False
                return data, cached
            else:
                print(f'ERROR: Google API HTTP status code was not OK ({response.status_code})')
                print(f'Google API response was: {data}')
                print('Returning null value')
                cached = False
                return None, cached

        except requests.exceptions.RequestException as e:
            # Handle connection or request errors
            print(f'ERROR: Request was not OK ({str(e)})')
            print('Returning null value')
            cached = False
            return None, cached


def obtener_nominatim_id_establecimiento(id_establecimiento, nocache=False):
    establecimiento = Establecimiento.objects.filter(id=id_establecimiento).first()
    if not establecimiento:
        logger.error(f'Obtaining Nominatim data: no establishment found with id {id_establecimiento}. Omitting.')
    else:
        metadatos_establecimiento = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first()
        if metadatos_establecimiento.nominatim_checked:
            # nocache ignores cached content and queries API again, no matter what
            if metadatos_establecimiento and not nocache:
                if metadatos_establecimiento.nominatim_checked > establecimiento.fecha_actualizacion:
                    logger.info(f'Using cached Nominatim results for establishment with id {id_establecimiento}.')
                    cached = True
                    return metadatos_establecimiento.nominatim_result, cached

        direccion = establecimiento.direccion
        poblacion = establecimiento.poblacion
        '''
        logger.debug(f'Obtaining Nominatim data. Will use the following data from establishment {id_establecimiento}: '
                     f'locality={poblacion}, address={direccion}')
        '''
        nominatim_viewbox = "40.522,0.158,42.868,3.327"  # --> Limit Nominatim results to Catalonia only.
        baseurl = 'https://nominatim.openstreetmap.org/search'
        urlparams = {
            'format': 'json',
            'street': f'{direccion}',
            'city': f'{poblacion}',
            'addressdetails': 1,
            'extratags': 1,
            'namedetails': 1,
            'countrycodes': 'es,ad',  # Spain and Andorra only
            'limit': 1,
            'viewbox': nominatim_viewbox,
            'key': settings.NOMINATIM_API_KEY
        }
        encoded_params = urlencode(urlparams)
        url = f'{baseurl}?{encoded_params}'
        logger.debug(f'Querying {url}')
        try:
            response = requests.get(url)
            data = response.text
            logger.debug(f'Query response: {data}')
        except Exception as e:
            result = {'error': f'While querying nominatim API: {e}'}
            logger.error(result)
            cached = False
            return result, cached
        if data:
            cached = False
            return data, cached
        else:
            logger.warning('No data returned from query.')
            cached = False
            return {}, cached


def establecimientos_sin_coordenadas():
    # Dirty but acceptable. And makes (non-expert) user's life easier. 0, 0 means "not calculated".
    queryset_establecimientos_sin_coordenadas = (
            Establecimiento.objects.filter(latitud=0) &
            Establecimiento.objects.filter(longitud=0)
    )
    queryset_establecimientos_sin_coordenadas = queryset_establecimientos_sin_coordenadas.filter(activo=True)

    establecimientos_sin_coordenadas_dict = {}
    for establecimiento in queryset_establecimientos_sin_coordenadas:
        establecimientos_sin_coordenadas_dict[establecimiento.id] = establecimiento.nombre
    if len(establecimientos_sin_coordenadas_dict) > 0:
        logger.info(f'The following establishments have no valid GPS coords, so we will try to obtain them: '
                    f'{establecimientos_sin_coordenadas_dict}')
        return establecimientos_sin_coordenadas_dict
    else:
        logger.info('No establishments found with GPS coords pending calculation.')
        return {}


def establecimientos_sin_cp():
    queryset_establecimientos_sin_cp = (
            Establecimiento.objects.filter(codigo_postal__isnull=True) |
            Establecimiento.objects.filter(codigo_postal='')
    )
    queryset_establecimientos_sin_cp = queryset_establecimientos_sin_cp.filter(activo=True)
    establecimientos_sin_cp_dict = {}
    for establecimiento in queryset_establecimientos_sin_cp:
        establecimientos_sin_cp_dict[establecimiento.id] = establecimiento.nombre
    if len(establecimientos_sin_cp_dict) > 0:
        logger.info(f'The following establishments had no valid postal code, so we will request it: '
                    f'{establecimientos_sin_cp_dict}')
        return establecimientos_sin_cp_dict
    else:
        logger.info('No establishments found with empty postal codes.')
        return {}


def anadir_metadatos_google_establecimiento(id_establecimiento, google_data):
    date_of_check = timezone.now()
    lookup_objeto = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first()
    if lookup_objeto:
        logger.info(f'Updating metadata entry for establishment {id_establecimiento}')
        lookup_objeto.google_checked = date_of_check
        lookup_objeto.google_result = google_data
        lookup_objeto.save()
    else:
        logger.info(f'Creating metadata entry for establishment {id_establecimiento}')
        new_metadata = MetadatosEstablecimiento(id=Establecimiento.objects.filter(id=id_establecimiento).first(),
                                                google_checked=date_of_check, google_result=google_data)
        new_metadata.save()
        logger.debug(f'New Google metadata saved for id {id_establecimiento}')


def anadir_metadatos_nominatim_establecimiento(id_establecimiento, nominatim_data):
    date_of_check = timezone.now()
    lookup_objeto = MetadatosEstablecimiento.objects.filter(id=id_establecimiento).first()
    if lookup_objeto:
        logger.info(f'Updating metadata entry for establishment {id_establecimiento}')
        lookup_objeto.nominatim_checked = date_of_check
        lookup_objeto.nominatim_result = nominatim_data
        lookup_objeto.save()
    else:
        logger.info(f'Creating metadata entry for establishment {id_establecimiento}')
        new_metadata = MetadatosEstablecimiento(id=Establecimiento.objects.filter(id=id_establecimiento).first(),
                                                nominatim_checked=date_of_check, nominatim_result=nominatim_data)
        new_metadata.save()
        logger.debug(f'New Nominatim metadata saved for id {id_establecimiento}')


class Command(BaseCommand):
    help = "Queries external geocoding APIs to complete the GPS coords or postal codes of establishments " \
           "that don't have valid ones."

    def add_arguments(self, parser):
        # Agregar argumentos posicionales
        parser.add_argument('--nocache', action='store_true',
                            help='Forces the script to requery the APIs, ignoring cached data')

    def handle(self, *args, **options):
        nocache = False
        lista_establecimientos_gps = establecimientos_sin_coordenadas()
        lista_establecimientos_cp = establecimientos_sin_cp()
        lista_establecimientos_todo = {**lista_establecimientos_gps, **lista_establecimientos_cp}
        if len(lista_establecimientos_todo) > 0:
            logger.info('Requesting Nominatim data for establishments with either missing GPS coords '
                        'or missing postal code.')
            nocache = options['nocache']
            if nocache:
                logger.debug('Ignoring cached API responses as per user request.')
        for id_establecimiento, nombre_establecimiento in lista_establecimientos_todo.items():
            nominatim_data, cached = obtener_nominatim_id_establecimiento(id_establecimiento, nocache=nocache)
            if not cached:
                anadir_metadatos_nominatim_establecimiento(id_establecimiento, nominatim_data)
        if lista_establecimientos_gps:
            logger.info('Parsing GPS coords from Nominatim for establishments needing it.')
            for id_establecimiento, nombre_establecimiento in lista_establecimientos_gps.items():
                actualizar_coordenadas_desde_nominatim(id_establecimiento)
        if lista_establecimientos_cp:
            logger.info('Parsing postal codes from Nominatim for establishments needing it.')
            for id_establecimiento, nombre_establecimiento in lista_establecimientos_cp.items():
                actualizar_cp_desde_nominatim(id_establecimiento)

        # PASS TWO: Google Maps as last resort to get the data that Nominatim failed to get

        lista_establecimientos_gps = establecimientos_sin_coordenadas()
        lista_establecimientos_cp = establecimientos_sin_cp()
        lista_establecimientos_todo = {**lista_establecimientos_gps, **lista_establecimientos_cp}
        if len(lista_establecimientos_todo) > 0:
            logger.info('Requesting Google Places data for establishments that still have missing either GPS coords '
                        'or missing postal code.')
        for id_establecimiento, nombre_establecimiento in lista_establecimientos_todo.items():
            google_data, cached = obtener_google_id_establecimiento(id_establecimiento, nocache=nocache)
            if not cached:
                anadir_metadatos_google_establecimiento(id_establecimiento, google_data)

        if lista_establecimientos_gps:
            logger.info('Parsing GPS coords from Google Places for establishments needing it.')
            for id_establecimiento, nombre_establecimiento in lista_establecimientos_gps.items():
                actualizar_coordenadas_desde_google(id_establecimiento)
        """
        if lista_establecimientos_cp:
            logger.info('Parsing postal codes from Google Places for establishments needing it.')
            for id_establecimiento, nombre_establecimiento in lista_establecimientos_cp.items():
                actualizar_cp_desde_google(id_establecimiento)
        """
