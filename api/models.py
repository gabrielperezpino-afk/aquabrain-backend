from django.db import models

class Huerta(models.Model):
    ESTADO_CHOICES = [
        ('ONLINE', 'Online (En línea)'),
        ('OFFLINE', 'Offline (Desconectado)'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Huerta")
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación Física")
    esp32_device_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID Microcontrolador ESP32",
        help_text="Ej: ESP32-S3-AQUA-01"
    )
    cultivo_activo = models.CharField(max_length=50, default="Rúcula", verbose_name="Cultivo Activo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ONLINE', verbose_name="Estado de Conexión")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Alta")
    ultimo_reporte = models.DateTimeField(auto_now=True, verbose_name="Último Reporte")

    class Meta:
        verbose_name = "Huerta"
        verbose_name_plural = "Huertas"
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre} ({self.esp32_device_id}) - {self.cultivo_activo}"


class Receta(models.Model):
    cultivo = models.CharField(max_length=50, unique=True, verbose_name="Cultivo / Variedad")
    tr_dia = models.IntegerField(default=15, verbose_name="Tiempo Riego Día (seg)")
    td_dia = models.IntegerField(default=240, verbose_name="Tiempo Descanso Día (seg)")
    tr_noche = models.IntegerField(default=10, verbose_name="Tiempo Riego Noche (seg)")
    td_noche = models.IntegerField(default=480, verbose_name="Tiempo Descanso Noche (seg)")
    modo_manual = models.BooleanField(default=False, verbose_name="Modo Manual")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Receta de Riego"
        verbose_name_plural = "Recetas de Riego"

    def __str__(self):
        return f"Receta {self.cultivo} (TR: {self.tr_dia}s / TD: {self.td_dia}s)"


class Telemetria(models.Model):
    ESTADO_AGUA_CHOICES = [
        ('WATER_OK', 'WATER_OK - Nivel Adecuado (>10%)'),
        ('WATER_LOW', 'WATER_LOW - Nivel Bajo (<=10%)'),
        ('WATER_EMPTY', 'WATER_EMPTY - Tanque Vacío (<=5%)'),
    ]

    huerta = models.ForeignKey(Huerta, on_delete=models.CASCADE, related_name='telemetrias', verbose_name="Huerta")
    temperatura = models.FloatField(verbose_name="Temperatura (°C)")
    humedad = models.FloatField(verbose_name="Humedad Relativa (%)")
    nivel_agua = models.IntegerField(verbose_name="Nivel de Agua (%)")
    estado_agua = models.CharField(max_length=20, choices=ESTADO_AGUA_CHOICES, default='WATER_OK', verbose_name="Estado Hídrico")
    bomba_activa = models.BooleanField(default=False, verbose_name="Estado Bomba")
    vpd = models.FloatField(null=True, blank=True, verbose_name="VPD (kPa)")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Lectura de Telemetría"
        verbose_name_plural = "Historial de Telemetría"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.huerta.nombre} - T:{self.temperatura}°C H:{self.humedad}% Agua:{self.nivel_agua}%"


class Bitacora(models.Model):
    huerta = models.ForeignKey(Huerta, on_delete=models.CASCADE, related_name='bitacoras', verbose_name="Huerta")
    usuario = models.CharField(max_length=150, verbose_name="Autor")
    rol = models.CharField(max_length=50, default="Encargado", verbose_name="Rol")
    cultivo = models.CharField(max_length=50, verbose_name="Cultivo Observado")
    observacion = models.TextField(verbose_name="Nota u Observación Técnica")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Entrada de Bitácora"
        verbose_name_plural = "Bitácora de Cultivo"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} ({self.rol}) - {self.cultivo} [{self.fecha.strftime('%d/%m/%Y %H:%M')}]"


class Auditoria(models.Model):
    CATEGORIA_CHOICES = [
        ('BOMBA', 'Bomba de Riego'),
        ('RECETA', 'Receta / Parámetros'),
        ('ALERTA', 'Alerta / Contingencia'),
        ('SISTEMA', 'Sistema Operativo'),
        ('SEGURIDAD', 'Seguridad y Acceso'),
        ('HUERTA', 'Gestión de Huerta'),
    ]

    usuario = models.CharField(max_length=150, verbose_name="Usuario / Sistema")
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, verbose_name="Categoría")
    descripcion = models.TextField(verbose_name="Descripción del Evento")
    ip_origen = models.CharField(max_length=50, blank=True, null=True, verbose_name="IP de Origen")
    fecha = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Evento de Auditoría"
        verbose_name_plural = "Registro de Auditoría"
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.categoria}] {self.usuario}: {self.descripcion[:50]}"
