from rest_framework import serializers
from .models import Huerta, Receta, Telemetria, Bitacora, Auditoria
import math

class HuertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huerta
        fields = '__all__'


class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = '__all__'


class TelemetriaSerializer(serializers.ModelSerializer):
    huerta_nombre = serializers.ReadOnlyField(source='huerta.nombre')

    class Meta:
        model = Telemetria
        fields = '__all__'


class BitacoraSerializer(serializers.ModelSerializer):
    huerta_nombre = serializers.ReadOnlyField(source='huerta.nombre')

    class Meta:
        model = Bitacora
        fields = '__all__'


class AuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditoria
        fields = '__all__'


class IngestTelemetriaSerializer(serializers.Serializer):
    """
    Serializer optimizado para el firmware ESP32 (tramas JSON compactas según RNF05).
    Permite enviar datos usando el ID del microcontrolador directamente.
    """
    esp32_device_id = serializers.CharField(max_length=50)
    temperatura = serializers.FloatField()
    humedad = serializers.FloatField()
    nivel_agua = serializers.IntegerField(min_value=0, max_value=100)
    bomba_activa = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        device_id = validated_data['esp32_device_id']
        temp = validated_data['temperatura']
        hum = validated_data['humedad']
        nivel = validated_data['nivel_agua']
        bomba = validated_data.get('bomba_activa', False)

        # Buscar o crear la huerta correspondiente
        huerta, _ = Huerta.objects.get_or_create(
            esp32_device_id=device_id,
            defaults={
                'nombre': f'Huerta {device_id}',
                'ubicacion': 'Instalación Principal AquaPlants',
                'cultivo_activo': 'Rúcula',
                'estado': 'ONLINE'
            }
        )

        # Regla de clasificación hídrica estricta (RF10 y RNF09)
        if nivel <= 5:
            estado_agua = 'WATER_EMPTY'
            # Bloqueo forzado preventivo de la bomba
            bomba = False
        elif nivel <= 10:
            estado_agua = 'WATER_LOW'
        else:
            estado_agua = 'WATER_OK'

        # Cálculo agronómico en el servidor de VPD (Déficit de Presión de Vapor en kPa)
        # VPD = VPsat * (1 - RH / 100), donde VPsat = 0.61078 * exp((17.27 * T) / (T + 237.3))
        try:
            vp_sat = 0.61078 * math.exp((17.27 * temp) / (temp + 237.3))
            vpd = round(vp_sat * (1.0 - (hum / 100.0)), 2)
        except Exception:
            vpd = None

        # Guardar en base de datos PostgreSQL en Neon
        telemetria = Telemetria.objects.create(
            huerta=huerta,
            temperatura=temp,
            humedad=hum,
            nivel_agua=nivel,
            estado_agua=estado_agua,
            bomba_activa=bomba,
            vpd=vpd
        )

        # Actualizar último reporte y estado de la huerta
        huerta.estado = 'ONLINE'
        huerta.save(update_fields=['estado', 'ultimo_reporte'])

        # Si el agua está vacía, registrar auditoría automática
        if estado_agua == 'WATER_EMPTY':
            Auditoria.objects.create(
                usuario=f"ESP32 ({device_id})",
                categoria='ALERTA',
                descripcion=f"ALERTA CRÍTICA: Tanque vacío ({nivel}%). Bloqueo preventivo de bomba activado."
            )

        return telemetria
