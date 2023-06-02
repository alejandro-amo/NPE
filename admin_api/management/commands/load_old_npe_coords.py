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
        df.sort_values('id', inplace=True)  # Ordenar por la columna 'id'
        df.reset_index(drop=True, inplace=True)  # Eliminar los índices y restablecerlos
        # Some fixes to data types
        df['latitud'] = df['latitud'].fillna(value=0)
        df['longitud'] = df['longitud'].fillna(value=0)

        fecha = timezone.now()
        for index, row in df.iterrows():
            # print(f'Working on item: {index+1} - {row["name"]}')
            id = row['id']
            latitud = float(row['latitud'])
            longitud = float(row['longitud'])
            # creado_por = 'Importador de datos antiguos'
            # fecha_creacion = fecha_creacion,
            actualizado_por = 'Calculador de coordenadas GPS'
            fecha_actualizacion = fecha
            establecimiento = Establecimiento.objects.all().filter(id=id).first()
            if establecimiento:
                if establecimiento.latitud == 0 and establecimiento.longitud == 0:
                    establecimiento.latitud = latitud
                    establecimiento.longitud = longitud
                    establecimiento.save()
                    logger.info(f'Adding coords ({latitud},{longitud}) to id {id}')


