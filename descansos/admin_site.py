"""AdminSite custom: expone Dashboard, Pacientes y Carga de Excel como
páginas dentro de /admin/ y los agrupa en una sección "Reportes" del sidebar.

Implementación basada en los hooks oficiales de Django:
- get_urls(): añade URLs custom
- get_app_list(): inyecta una "app sintética" para agrupar los reportes
- admin_view(): envuelve auth/staff_required automáticamente
"""

from django.urls import path, reverse
from unfold.sites import UnfoldAdminSite


class ReporteAdminSite(UnfoldAdminSite):
    site_header = 'Reporte de Descansos Médicos'
    site_title = 'Reporte DM'
    index_title = 'Panel'

    def get_urls(self):
        # Import diferido para romper el ciclo views.py ↔ admin_site.py.
        from . import views

        urls = super().get_urls()
        custom = [
            path('dashboard/', self.admin_view(views.dashboard_view), name='dashboard'),
            path('pacientes/', self.admin_view(views.pacientes_view), name='pacientes'),
            path('upload/', self.admin_view(views.upload_view), name='upload'),
            path('api/dias-por-gerencia/', self.admin_view(views.api_dias_por_gerencia), name='api_dias_por_gerencia'),
            path('api/ranking-motivos/', self.admin_view(views.api_ranking_motivos), name='api_ranking_motivos'),
            path('api/tendencia-mensual/', self.admin_view(views.api_tendencia_mensual), name='api_tendencia_mensual'),
            path('api/top-pacientes/', self.admin_view(views.api_top_pacientes), name='api_top_pacientes'),
            path('api/paciente/<str:codigo>/', self.admin_view(views.api_paciente_detalle), name='api_paciente_detalle'),
            path('api/paciente/<str:codigo>/telefono/', self.admin_view(views.api_paciente_actualizar_telefono), name='api_paciente_actualizar_telefono'),
            path('api/paciente/<str:codigo>/seguimiento/', self.admin_view(views.api_seguimiento_crear), name='api_seguimiento_crear'),
        ]
        return custom + urls

    def get_app_list(self, request, app_label=None):
        # Lista nativa de apps con modelos registrados.
        app_list = super().get_app_list(request, app_label)

        # Sección sintética "Reportes" — sus "modelos" en realidad son URLs custom.
        # Si se está filtrando por app específica, no la inyectamos.
        if app_label and app_label != 'reportes':
            return app_list

        view_perms = {'add': False, 'change': False, 'delete': False, 'view': True}
        reportes = {
            'name': 'Reportes',
            'app_label': 'reportes',
            'app_url': reverse('admin:dashboard'),
            'has_module_perms': True,
            'models': [
                {
                    'name': 'Dashboard',
                    'object_name': 'Dashboard',
                    'admin_url': reverse('admin:dashboard'),
                    'view_only': True,
                    'perms': view_perms,
                },
                {
                    'name': 'Pacientes',
                    'object_name': 'Pacientes',
                    'admin_url': reverse('admin:pacientes'),
                    'view_only': True,
                    'perms': view_perms,
                },
                {
                    'name': 'Cargar Excel',
                    'object_name': 'Upload',
                    'admin_url': reverse('admin:upload'),
                    'view_only': True,
                    'perms': view_perms,
                },
            ],
        }
        return [reportes] + app_list


reporte_admin_site = ReporteAdminSite(name='admin')
