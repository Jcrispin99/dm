from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from .admin_site import reporte_admin_site
from .models import DescansoMedico, Gerencia, Motivo, Paciente, Seguimiento


class GerenciaListFilter(admin.SimpleListFilter):
    title = 'gerencia'
    parameter_name = 'gerencia'

    def lookups(self, request, model_admin):
        return [(g.id, g.nombre) for g in Gerencia.objects.order_by('nombre')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(gerencia_id=self.value())
        return queryset


class MotivoListFilter(admin.SimpleListFilter):
    """Filtra los motivos según la gerencia seleccionada en el filtro de gerencia."""
    title = 'motivo'
    parameter_name = 'motivo'

    def lookups(self, request, model_admin):
        motivos = Motivo.objects.all()
        gerencia_id = request.GET.get('gerencia')
        if gerencia_id:
            motivos = motivos.filter(descansos__gerencia_id=gerencia_id).distinct()
        return [(m.id, m.nombre) for m in motivos.order_by('nombre')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(motivo_id=self.value())
        return queryset


class GerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    list_per_page = 20


class MotivoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    list_per_page = 20


class PacienteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'telefono')
    search_fields = ('codigo', 'nombre', 'telefono')
    list_per_page = 20


class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha', 'medio', 'estado', 'proximo_contacto', 'usuario')
    list_filter = ('medio', 'estado', 'fecha', 'usuario')
    search_fields = ('paciente__codigo', 'paciente__nombre', 'notas')
    readonly_fields = ('creado_en',)
    autocomplete_fields = ('paciente',)
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


class DescansoMedicoAdmin(admin.ModelAdmin):
    list_display = (
        'paciente', 'gerencia', 'fecha_inicio', 'fecha_fin', 'dias', 'motivo', 'cargado_en',
    )
    list_filter = (GerenciaListFilter, MotivoListFilter, 'fecha_inicio')
    search_fields = ('paciente__codigo', 'paciente__nombre', 'observaciones')
    readonly_fields = ('dias', 'cargado_en')
    list_per_page = 20


reporte_admin_site.register(Gerencia, GerenciaAdmin)
reporte_admin_site.register(Motivo, MotivoAdmin)
reporte_admin_site.register(Paciente, PacienteAdmin)
reporte_admin_site.register(DescansoMedico, DescansoMedicoAdmin)
reporte_admin_site.register(Seguimiento, SeguimientoAdmin)
reporte_admin_site.register(User, UserAdmin)
reporte_admin_site.register(Group, GroupAdmin)
