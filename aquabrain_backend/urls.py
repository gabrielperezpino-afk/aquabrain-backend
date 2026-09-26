from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
import os

def simulador_view(request):
    """
    Sirve la interfaz web interactiva del simulador de hardware ESP32 / Arduino
    para que cualquier persona pueda probar el sistema desde su navegador o teléfono celular.
    """
    html_path = os.path.join(settings.BASE_DIR, 'simulador_esp32.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html; charset=utf-8')
    return HttpResponse("Simulador no encontrado", status=404)

urlpatterns = [
    path('', simulador_view, name='home_simulador'),
    path('simulador/', simulador_view, name='simulador'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

admin.site.site_header = "AquaBrain 2026 - Administración"
admin.site.site_title = "AquaBrain 2026 Portal"
admin.site.index_title = "Gestión Centralizada de Huertas Inteligentes AquaPlants"
