"""
Script de simulación de lecturas de sensores ESP32 hacia la base de datos en la nube (Neon PostgreSQL).
Inserta lecturas de temperatura (AHT), humedad, nivel de agua ultrasónico (HC-SR04) y bitácora técnica.
"""
import os
import django
import random
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aquabrain_backend.settings')
django.setup()

from api.models import Huerta, Telemetria, Bitacora, Auditoria

def ejecutar_prueba():
    print("==========================================================")
    print("   AQUABRAIN 2026 — PRUEBA DE CONEXIÓN A LA NUBE (NEON)   ")
    print("==========================================================")

    huerta = Huerta.objects.get(esp32_device_id='ESP32-S3-AQUA-01')
    print(f"\n[1] Huerta seleccionada: {huerta.nombre} ({huerta.esp32_device_id})")

    # Generar 5 lecturas de sensores simulando el ESP32
    print("\n[2] Insertando lecturas de telemetría de sensores en Neon Cloud:")
    niveles = [95, 88, 82, 10, 4]  # Incluye WATER_OK, WATER_LOW y WATER_EMPTY
    
    for i, nivel in enumerate(niveles, 1):
        temp = round(random.uniform(21.0, 24.5), 1)
        hum = round(random.uniform(60.0, 75.0), 1)
        bomba = (i % 2 == 1) and (nivel > 5)

        # Clasificación hídrica RF10 / RNF09
        if nivel <= 5:
            estado_agua = 'WATER_EMPTY'
            bomba = False
        elif nivel <= 10:
            estado_agua = 'WATER_LOW'
        else:
            estado_agua = 'WATER_OK'

        # VPD aproximado
        vpd = round(0.61078 * (2.718 ** ((17.27 * temp) / (temp + 237.3))) * (1.0 - (hum / 100.0)), 2)

        tele = Telemetria.objects.create(
            huerta=huerta,
            temperatura=temp,
            humedad=hum,
            nivel_agua=nivel,
            estado_agua=estado_agua,
            bomba_activa=bomba,
            vpd=vpd
        )
        print(f"  -> Lectura #{i} guardada en Neon ID:{tele.id} | Temp: {temp}°C | Hum: {hum}% | Nivel: {nivel}% ({estado_agua}) | Bomba: {'ON' if bomba else 'OFF'}")

    # Insertar nota de bitácora
    print("\n[3] Registrando entrada de bitácora técnica de cultivo:")
    bit = Bitacora.objects.create(
        huerta=huerta,
        usuario="Gabriel (Encargado)",
        rol="Encargado",
        cultivo="Rúcula",
        observacion="Inspección visual realizada: raíces blancas y sanas. Pulverización por niebla aeropónica funcionando con ciclo 15s/240s."
    )
    print(f"  -> Bitácora guardada en Neon ID:{bit.id}: '{bit.observacion[:60]}...'")

    # Insertar evento de auditoría
    print("\n[4] Registrando evento de auditoría:")
    aud = Auditoria.objects.create(
        usuario="admin@aquaplants.cl",
        categoria="SISTEMA",
        descripcion="Verificación inicial de conexión y persistencia a base de datos PostgreSQL en la nube Neon.tech exitosa."
    )
    print(f"  -> Auditoría guardada en Neon ID:{aud.id}: '{aud.descripcion}'")

    print("\n" + "="*58)
    print("  ¡ÉXITO TOTAL! Los datos ya están guardados en tu nube Neon.")
    print("  Ya puedes ir a tu navegador en console.neon.tech y verlos.")
    print("="*58)

if __name__ == '__main__':
    ejecutar_prueba()
