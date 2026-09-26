from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Huerta, Receta, Telemetria, Bitacora, Auditoria
from .serializers import (
    HuertaSerializer, RecetaSerializer, TelemetriaSerializer,
    BitacoraSerializer, AuditoriaSerializer, IngestTelemetriaSerializer
)
from django.utils import timezone
from datetime import timedelta

class HuertaViewSet(viewsets.ModelViewSet):
    queryset = Huerta.objects.all()
    serializer_class = HuertaSerializer

    @action(detail=False, methods=['get'])
    def verificar_offline(self, request):
        """
        RF29: Detección automática de dispositivos en estado OFFLINE
        si superan el umbral configurado (> 5 minutos sin reportar).
        """
        umbral = timezone.now() - timedelta(minutes=5)
        huertas = Huerta.objects.all()
        actualizadas = 0
        for h in huertas:
            if h.ultimo_reporte and h.ultimo_reporte < umbral and h.estado == 'ONLINE':
                h.estado = 'OFFLINE'
                h.save(update_fields=['estado'])
                actualizadas += 1
                Auditoria.objects.create(
                    usuario="Sistema Monitor",
                    categoria='HUERTA',
                    descripcion=f"Huerta {h.nombre} pasó a estado OFFLINE (> 5 min sin reportar)."
                )
        return Response({"status": "ok", "huertas_pasadas_a_offline": actualizadas})


class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer


class TelemetriaViewSet(viewsets.ModelViewSet):
    queryset = Telemetria.objects.all()
    serializer_class = TelemetriaSerializer

    def get_queryset(self):
        """
        Filtros de telemetría (RF12 y RF13):
        - Por huerta: ?huerta_id=1 o ?esp32_device_id=ESP32-S3-AQUA-01
        - Por rango de fechas: ?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
        - Últimas N lecturas: ?limit=50
        """
        qs = Telemetria.objects.all()
        huerta_id = self.request.query_params.get('huerta_id')
        device_id = self.request.query_params.get('esp32_device_id')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        limit = self.request.query_params.get('limit')

        if huerta_id:
            qs = qs.filter(huerta_id=huerta_id)
        if device_id:
            qs = qs.filter(huerta__esp32_device_id=device_id)
        if fecha_inicio:
            qs = qs.filter(timestamp__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(timestamp__date__lte=fecha_fin)

        if limit:
            try:
                qs = qs[:int(limit)]
            except ValueError:
                pass

        return qs

    @action(detail=False, methods=['post'])
    def ingesta_esp32(self, request):
        """
        Endpoint directo para microcontroladores ESP32 (POST /api/telemetria/ingesta_esp32/)
        JSON esperado:
        {
            "esp32_device_id": "ESP32-S3-AQUA-01",
            "temperatura": 22.4,
            "humedad": 65.2,
            "nivel_agua": 85,
            "bomba_activa": true
        }
        """
        serializer = IngestTelemetriaSerializer(data=request.data)
        if serializer.is_valid():
            telemetria = serializer.save()
            return Response({
                "status": "success",
                "message": "Telemetría almacenada exitosamente en Neon PostgreSQL",
                "data": TelemetriaSerializer(telemetria).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
