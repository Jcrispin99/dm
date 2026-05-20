from django.urls import path

from . import views

app_name = 'descansos'

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/dias-por-gerencia/', views.api_dias_por_gerencia, name='api_dias_por_gerencia'),
    path('api/ranking-motivos/', views.api_ranking_motivos, name='api_ranking_motivos'),
    path('api/tendencia-mensual/', views.api_tendencia_mensual, name='api_tendencia_mensual'),
    path('api/top-pacientes/', views.api_top_pacientes, name='api_top_pacientes'),
]
