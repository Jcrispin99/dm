from django.db import models


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
