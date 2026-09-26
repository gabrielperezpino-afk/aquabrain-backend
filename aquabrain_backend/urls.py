from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

admin.site.site_header = "AquaBrain 2026 - Administración"
admin.site.site_title = "AquaBrain 2026 Portal"
admin.site.index_title = "Gestión Centralizada de Huertas Inteligentes AquaPlants"
