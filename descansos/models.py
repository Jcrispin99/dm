from django.conf import settings
from django.db import models
from django.utils import timezone


class Gerencia(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Gerencias'

    def __str__(self):
        return self.nombre


class Motivo(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Motivo (Clasificación)'
        verbose_name_plural = 'Motivos (Clasificación)'

    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    codigo = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class DescansoMedico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='descansos')
    gerencia = models.ForeignKey(Gerencia, on_delete=models.PROTECT, related_name='descansos')
    motivo = models.ForeignKey(Motivo, on_delete=models.PROTECT, related_name='descansos')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True, default='')
    archivo_origen = models.CharField(max_length=255, blank=True, default='')
    cargado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio', 'paciente__nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['paciente', 'fecha_inicio', 'fecha_fin'],
                name='uniq_descanso_paciente_periodo',
            ),
        ]
        indexes = [
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['gerencia']),
            models.Index(fields=['motivo']),
        ]

    def save(self, *args, **kwargs):
        self.dias = (self.fecha_fin - self.fecha_inicio).days + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.paciente} ({self.fecha_inicio} → {self.fecha_fin})'


class Seguimiento(models.Model):
    MEDIO_LLAMADA = 'llamada'
    MEDIO_WHATSAPP = 'whatsapp'
    MEDIO_PRESENCIAL = 'presencial'
    MEDIO_OTRO = 'otro'
    MEDIO_CHOICES = [
        (MEDIO_LLAMADA, 'Llamada'),
        (MEDIO_WHATSAPP, 'WhatsApp'),
        (MEDIO_PRESENCIAL, 'Presencial'),
        (MEDIO_OTRO, 'Otro'),
    ]

    ESTADO_CONTACTADO = 'contactado'
    ESTADO_SIN_RESPUESTA = 'sin_respuesta'
    ESTADO_NUMERO_ERRONEO = 'numero_erroneo'
    ESTADO_NO_DISPONIBLE = 'no_disponible'
    ESTADO_OTRO = 'otro'
    ESTADO_CHOICES = [
        (ESTADO_CONTACTADO, 'Contactado'),
        (ESTADO_SIN_RESPUESTA, 'Sin respuesta'),
        (ESTADO_NUMERO_ERRONEO, 'Número erróneo'),
        (ESTADO_NO_DISPONIBLE, 'No disponible'),
        (ESTADO_OTRO, 'Otro'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='seguimientos')
    fecha = models.DateTimeField(default=timezone.now)
    medio = models.CharField(max_length=20, choices=MEDIO_CHOICES, default=MEDIO_LLAMADA)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_CONTACTADO)
    notas = models.TextField(blank=True, default='')
    proximo_contacto = models.DateField(null=True, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='seguimientos_registrados',
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [models.Index(fields=['paciente', '-fecha'])]
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'

    def __str__(self):
        return f'{self.paciente} · {self.fecha:%Y-%m-%d %H:%M} · {self.get_estado_display()}'
