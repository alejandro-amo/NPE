from rest_framework import serializers
from .models import Establecimiento, TipoEstablecimiento
from datetime import datetime
from django.utils import timezone


class EstablecimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establecimiento
        fields = ('id', 'activo', 'tipo_establecimiento', 'nombre', 'direccion', 'codigo_postal', 'poblacion',
                  'latitud', 'longitud', 'telefonos', 'email', 'web', 'creado_por', 'actualizado_por', 'fecha_creacion',
                  'fecha_actualizacion', 'observaciones')
        read_only_fields = ('id', 'creado_por', 'actualizado_por', 'fecha_creacion', 'fecha_actualizacion',
                            'google_maps_id')

    def create(self, validated_data):
        username = self.context['request'].user.username
        validated_data['creado_por'] = username
        validated_data['fecha_creacion'] = timezone.now()
        validated_data['activo'] = 1
        return super().create(validated_data)

    def update(self, instance, validated_data):
        username = self.context['request'].user.username
        validated_data['actualizado_por'] = username
        validated_data['fecha_actualizacion'] = datetime.today()
        return super().update(instance, validated_data)

