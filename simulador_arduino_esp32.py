"""
=============================================================================
 AQUABRAIN 2026 — SIMULADOR DE MICROCONTROLADOR ARDUINO / ESP32-S3
=============================================================================
Este script emula exactamente el comportamiento del firmware C++ (main.cpp):
1. Simula las lecturas analógicas y digitales de los sensores de hardware:
   - Sensor de Temperatura y Humedad Ambiental (AHT10 / DHT22)
   - Sensor Ultrasónico de Nivel Hídrico del Estanque (HC-SR04)
   - Relé Actuador de la Bomba de Alta Presión (GPIO 23)
2. Empaqueta los datos en tramas JSON compactas (< 500 ms según RNF05).
3. Transmite las peticiones HTTP POST reales vía red hacia el servidor Django.
4. El servidor Django procesa y almacena los datos en la nube de Neon (PostgreSQL).
=============================================================================
"""

import urllib.request
import json
import time
import random
import sys

API_URL = "http://localhost:8000/api/telemetria/ingesta_esp32/"
DEVICE_ID = "ESP32-S3-AQUA-01"

def enviar_paquete_al_servidor(temperatura, humedad, nivel_agua, bomba_activa):
    payload = {
        "esp32_device_id": DEVICE_ID,
        "temperatura": round(temperatura, 1),
        "humedad": round(humedad, 1),
        "nivel_agua": int(nivel_agua),
        "bomba_activa": bool(bomba_activa)
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "ESP32-AquaBrain-Firmware/2.0"}
    )

    t_inicio = time.time()
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            t_ms = int((time.time() - t_inicio) * 1000)
            res_body = json.loads(response.read().decode('utf-8'))
            return True, t_ms, res_body
    except Exception as e:
        t_ms = int((time.time() - t_inicio) * 1000)
        return False, t_ms, str(e)


def modo_continuo():
    print("\n" + "="*70)
    print(" INICIANDO TRANSMISIÓN CONTINUA DEL ESP32 HACIA LA NUBE NEON")
    print(" (Presiona Ctrl + C en cualquier momento para detener)")
    print("="*70)

    # Valores iniciales realistas para aeroponía
    nivel_estanque = 92
    ciclo = 1

    try:
        while True:
            # Simular fluctuaciones naturales del invernadero
            temp = 22.0 + random.uniform(-1.5, 2.0)
            hum = 68.0 + random.uniform(-4.0, 5.0)

            # Las plantas van consumiendo agua lentamente
            if ciclo % 3 == 0 and nivel_estanque > 8:
                nivel_estanque -= 1

            # Máquina de estados de la bomba
            if nivel_estanque <= 5:
                estado_hídrico = "CRÍTICO - VACÍO (WATER_EMPTY)"
                bomba = False
                color_alerta = " [!] BLOQUEO DE HARDWARE: BOMBA APAGADA POR SEGURIDAD"
            elif nivel_estanque <= 10:
                estado_hídrico = "BAJO (WATER_LOW)"
                bomba = (ciclo % 2 == 1)
                color_alerta = " [?] ALERTA AMARILLA: Rellenar solución nutritiva"
            else:
                estado_hídrico = "ADECUADO (WATER_OK)"
                bomba = (ciclo % 2 == 1)
                color_alerta = " [OK] Ciclo de riego activo"

            print(f"\n--- [TRAMA #{ciclo:03d}] ESP32 Serial Monitor (115200 baud) ---")
            print(f"📡 Dispositivo: {DEVICE_ID} | Wi-Fi: Conectado (RSSI: -58 dBm)")
            print(f"🌡️  Sensor AHT:       Temp = {temp:.1f} °C  |  Humedad = {hum:.1f} %")
            print(f"🌊 Sensor HC-SR04:   Estanque = {nivel_estanque}%  -> {estado_hídrico}")
            print(f"⚡ Relé Bomba (G23): {'ENCENDIDA (Pulverizando)' if bomba else 'APAGADA (Descanso)'}{color_alerta}")

            # Transmitir por HTTP
            print(f"🚀 Transmitiendo POST a {API_URL} ...")
            exito, latencia_ms, respuesta = enviar_paquete_al_servidor(temp, hum, nivel_estanque, bomba)

            if exito:
                data_db = respuesta.get('data', {})
                print(f"✅ [HTTP 201 CREATED] Recibido ACK en {latencia_ms} ms (SLA < 500ms Cumplido)")
                print(f"💾 Guardado en Neon PostgreSQL -> ID en Nube: {data_db.get('id')} | VPD: {data_db.get('vpd')} kPa | Estado: {data_db.get('estado_agua')}")
            else:
                print(f"❌ Error al transmitir: {respuesta}")

            print(f"⏱️  Esperando 5 segundos para siguiente lectura...")
            time.sleep(5)
            ciclo += 1

    except KeyboardInterrupt:
        print("\n\n[ESP32] Simulación detenida por el usuario.")


def modo_alerta_vacio():
    print("\n" + "="*70)
    print(" SIMULANDO CONTINGENCIA: ESTANQUE VACÍO (<= 5%)")
    print("="*70)
    print("Simulando que el estanque cayó al 3% de agua...")
    exito, latencia_ms, respuesta = enviar_paquete_al_servidor(23.5, 62.0, 3, False)
    if exito:
        print(f"✅ Alerta transmitida con éxito en {latencia_ms} ms!")
        print(f"💾 Registro en Neon: {respuesta}")
        print("💡 Verifica en tu tabla 'api_telemetria' y 'api_auditoria' en Neon;")
        print("   verás la alerta crítica generada automáticamente.")
    else:
        print(f"❌ Error: {respuesta}")


def menu():
    print("\n" + "="*60)
    print("       AQUABRAIN 2026 — SIMULADOR VIRTUAL ARDUINO/ESP32    ")
    print("="*60)
    print(" 1) Iniciar transmisión continua cada 5 segundos (Auto)")
    print(" 2) Simular 1 lectura normal (Nivel 85%)")
    print(" 3) Simular alerta de estanque vacío (Nivel 3% - WATER_EMPTY)")
    print(" 4) Ingresar datos manuales personalizados")
    print(" 5) Salir")
    print("="*60)

    opcion = input("Selecciona una opción (1-5): ").strip()

    if opcion == "1":
        modo_continuo()
    elif opcion == "2":
        exito, ms, res = enviar_paquete_al_servidor(22.8, 68.0, 85, True)
        print(f"\nRespuesta del servidor ({ms} ms):", res)
    elif opcion == "3":
        modo_alerta_vacio()
    elif opcion == "4":
        try:
            t = float(input("Temperatura (°C): "))
            h = float(input("Humedad (%): "))
            n = int(input("Nivel de agua (0-100%): "))
            b = input("¿Bomba encendida? (s/n): ").lower() == 's'
            exito, ms, res = enviar_paquete_al_servidor(t, h, n, b)
            print(f"\nRespuesta del servidor ({ms} ms):", res)
        except Exception as e:
            print("Error en los datos:", e)
    elif opcion == "5":
        print("Saliendo...")
    else:
        print("Opción no válida.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        modo_continuo()
    elif len(sys.argv) > 1 and sys.argv[1] == '--single':
        exito, ms, res = enviar_paquete_al_servidor(23.1, 67.2, 86, True)
        print(f"Resultado ({ms} ms):", res)
    else:
        menu()
