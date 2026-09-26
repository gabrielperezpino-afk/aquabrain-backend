from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HuertaViewSet, RecetaViewSet, TelemetriaViewSet,
    BitacoraViewSet, AuditoriaViewSet
)

router = DefaultRouter()
router.register(r'huertas', HuertaViewSet, basename='huerta')
router.register(r'recetas', RecetaViewSet, basename='receta')
router.register(r'telemetria', TelemetriaViewSet, basename='telemetria')
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')
router.register(r'auditoria', AuditoriaViewSet, basename='auditoria')

urlpatterns = [
    path('', include(router.urls)),
]
