from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Poblacion(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class TipoEstablecimiento(models.Model):
    # id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Establecimiento(models.Model):
    # id = models.IntegerField(primary_key=True)
    activo = models.BooleanField(default=True)
    tipo_establecimiento = models.ForeignKey(TipoEstablecimiento, on_delete=models.SET_DEFAULT, default=1)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    codigo_postal = models.CharField(max_length=5, null=True, blank=True)
    poblacion = models.CharField(max_length=50, null=True, blank=True)
    # Latitud y longitud son a la vez datos del establecimiento (editables) y metadatos (calculados en segundo plano)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    email = models.CharField(max_length=255, null=True, blank=True)
    web = models.CharField(max_length=150, null=True, blank=True)
    telefonos = models.CharField(max_length=30, null=True, blank=True)
    creado_por = models.CharField(max_length=150, null=True, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, editable=False)
    actualizado_por = models.CharField(max_length=150, null=True, editable=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True, editable=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class MetadatosEstablecimiento(models.Model):
    id = models.OneToOneField(Establecimiento, primary_key=True, on_delete=models.CASCADE)
    # OpenStreetMaps Geocoding API (Nominatim) (checked daily for incomplete coords / postal codes in new items)
    nominatim_checked = models.DateTimeField(null=True, blank=True)
    nominatim_result = models.TextField(null=True, blank=True)  # Google places identifier
    # Google places/maps API (checked with low frequency to know operational status of the businesses)
    google_checked = models.DateTimeField(null=True, blank=True)
    google_result = models.TextField(null=True, blank=True)  #

    nombre_segun_google_candidato1 = models.TextField(null=True, blank=True)
    estado_segun_google_candidato1 = models.TextField(null=True, blank=True)
    nombre_segun_google_candidato2 = models.TextField(null=True, blank=True)
    estado_segun_google_candidato2 = models.TextField(null=True, blank=True)


class InternalData(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.TextField
