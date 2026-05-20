from django.contrib import admin

from .models import DescansoMedico, Gerencia, Motivo, Paciente


@admin.register(Gerencia)
class GerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(DescansoMedico)
class DescansoMedicoAdmin(admin.ModelAdmin):
    list_display = (
        'paciente', 'gerencia', 'fecha_inicio', 'fecha_fin', 'dias', 'motivo', 'cargado_en',
    )
    list_filter = ('gerencia', 'motivo', 'fecha_inicio')
    search_fields = ('paciente__codigo', 'paciente__nombre', 'observaciones')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('dias', 'cargado_en')
