import os

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone
import requests
from pathlib import Path
import pandas as pd
from urllib.parse import urlencode
from core import settings
from admin_api.models import Establecimiento, MetadatosEstablecimiento
import logging
logger = logging.getLogger(f'{settings.app_name}.{__name__}')


class Command(BaseCommand):
    help = "Loads data from an excel file template that has been properly filled."

    def handle(self, *args, **options):
        script_dir = Path(__file__).resolve().parent
        xlsxinputfile = script_dir.joinpath('..', '..', 'data', 'old_npe_data.xlsx')
        if Path.is_file(xlsxinputfile):
            logger.debug('XLSX file exists.')
        else:
            logger.error(f'XLSX file does not exist or path is not a file: {xlsxinputfile}')
            raise CommandError(1)
        logger.debug('Loading XLSX file')
        df = pd.read_excel(xlsxinputfile)
        logger.debug(f'XLSX file columns: {df.columns}')
        max_id = df['id'].max()
        logger.debug(f'Max ID for establishments: {max_id}')
        logger.debug('Creating auxiliary dataframe to fill the gaps in ID...')
        missing_ids = pd.DataFrame({'id': range(1, max_id+1)})
        logger.debug('Merging dfs...')
        df = df.merge(missing_ids, on='id', how='outer')
        df.sort_values('id', inplace=True)  # Ordenar por la columna 'id'
        df.reset_index(drop=True, inplace=True)  # Eliminar los índices y restablecerlos
        # Some fixes to data types
        df['active'] = df['active'].fillna(value=0)
        df['active'] = df['active'].astype('boolean')
        df['type'] = df['type'].fillna(value=1)
        df['type'] = df['type'].astype('int')
        df['type'] = df['type'].fillna(value=1)
        df['name'] = df['name'].fillna(value='---')
        df['address'] = df['address'].fillna(value='')
        df['postalcode'] = df['postalcode'].fillna(value='')
        df['city'] = df['city'].fillna(value='')
        df['phone'] = df['phone'].fillna(value='')
        df['email'] = df['email'].fillna(value='')
        df['web'] = df['web'].fillna(value='')
        df['lat'] = df['lat'].fillna(value=0)
        df['long'] = df['long'].fillna(value=0)

        fecha_creacion = timezone.now()
        for index, row in df.iterrows():
            print(f'Working on item: {index+1} - {row["name"]}')
            nombre = row['name']
            direccion = row['address']
            codigo_postal = str(row['postalcode']).strip()
            if codigo_postal == 0:
                codigo_postal = ''
            if len(codigo_postal) == 4:
                codigo_postal = f'0{codigo_postal}'
            '''
            # in case you want to import already existant coords
            latitud = row['latitud']
            longitud = row['longitud']
            '''
            # in case you want to recalculate after importing
            latitud = 0
            longitud = 0

            creado_por = 'Importador de datos antiguos'
            fecha_creacion = fecha_creacion,
            actualizado_por = None
            fecha_actualizacion = None
            poblacion = row['city']
            tipo_establecimiendo_id = row['type']
            activo = row['active']
            email = row['email']
            web = row['web']
            telefonos = row['phone']
            observaciones = ""
            # Actual creation of entry in DB
            nuevo_establecimiento = Establecimiento.objects.create(
                nombre=nombre,
                direccion=direccion,
                codigo_postal=codigo_postal,
                latitud=latitud,
                longitud=longitud,
                creado_por=creado_por,
                fecha_creacion=fecha_creacion,
                actualizado_por=actualizado_por,
                fecha_actualizacion=fecha_actualizacion,
                poblacion=poblacion,
                tipo_establecimiento_id=tipo_establecimiendo_id,
                activo=activo,
                email=email,
                web=web,
                telefonos=telefonos,
                observaciones=observaciones
            )
            nuevo_establecimiento.save()


