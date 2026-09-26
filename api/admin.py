from django.contrib import admin
from .models import Huerta, Receta, Telemetria, Bitacora, Auditoria

@admin.register(Huerta)
class HuertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion', 'esp32_device_id', 'cultivo_activo', 'estado', 'ultimo_reporte')
    list_filter = ('estado', 'cultivo_activo')
    search_fields = ('nombre', 'ubicacion', 'esp32_device_id')


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cultivo', 'tr_dia', 'td_dia', 'tr_noche', 'td_noche', 'modo_manual', 'fecha_actualizacion')
    list_filter = ('modo_manual',)
    search_fields = ('cultivo',)


@admin.register(Telemetria)
class TelemetriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'huerta', 'temperatura', 'humedad', 'nivel_agua', 'estado_agua', 'bomba_activa', 'vpd', 'timestamp')
    list_filter = ('estado_agua', 'bomba_activa', 'huerta')
    search_fields = ('huerta__nombre',)
    date_hierarchy = 'timestamp'


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'huerta', 'usuario', 'rol', 'cultivo', 'fecha')
    list_filter = ('rol', 'cultivo', 'huerta')
    search_fields = ('usuario', 'observacion')
    date_hierarchy = 'fecha'


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'usuario', 'descripcion', 'ip_origen', 'fecha')
    list_filter = ('categoria',)
    search_fields = ('usuario', 'descripcion')
    date_hierarchy = 'fecha'
