from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render

from .forms import UploadExcelForm
from .models import DescansoMedico, Gerencia
from .services.excel_loader import cargar_excel


def upload_view(request):
    result = None
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            result = cargar_excel(archivo, nombre_archivo=archivo.name)
    else:
        form = UploadExcelForm()
    return render(request, 'descansos/upload.html', {
        'form': form, 'result': result, 'active': 'upload',
    })


def dashboard_view(request):
    gerencias = Gerencia.objects.order_by('nombre')
    first = DescansoMedico.objects.order_by('fecha_inicio').values_list('fecha_inicio', flat=True).first()
    last = DescansoMedico.objects.order_by('-fecha_fin').values_list('fecha_fin', flat=True).first()
    return render(request, 'descansos/dashboard.html', {
        'gerencias': gerencias,
        'fecha_min': first or date.today(),
        'fecha_max': last or date.today(),
        'active': 'dashboard',
    })


def _apply_filters(qs, request):
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    gerencias = request.GET.getlist('gerencia')
    if fecha_desde:
        qs = qs.filter(fecha_inicio__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_fin__lte=fecha_hasta)
    if gerencias:
        qs = qs.filter(gerencia_id__in=gerencias)
    return qs


def api_dias_por_gerencia(request):
    qs = _apply_filters(DescansoMedico.objects.all(), request)
    data = (
        qs.values('gerencia__nombre')
        .annotate(total_dias=Sum('dias'), casos=Count('id'))
        .order_by('-total_dias')
    )
    return JsonResponse({
        'labels': [row['gerencia__nombre'] for row in data],
        'dias': [row['total_dias'] or 0 for row in data],
        'casos': [row['casos'] for row in data],
    })


def api_ranking_motivos(request):
    qs = _apply_filters(DescansoMedico.objects.all(), request)
    data = (
        qs.values('motivo__nombre')
        .annotate(total_dias=Sum('dias'), casos=Count('id'))
        .order_by('-total_dias')
    )
    return JsonResponse({
        'labels': [row['motivo__nombre'] for row in data],
        'dias': [row['total_dias'] or 0 for row in data],
        'casos': [row['casos'] for row in data],
    })


def api_tendencia_mensual(request):
    qs = _apply_filters(DescansoMedico.objects.all(), request)
    data = (
        qs.annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total_dias=Sum('dias'), casos=Count('id'))
        .order_by('mes')
    )
    return JsonResponse({
        'labels': [row['mes'].strftime('%Y-%m') if row['mes'] else '' for row in data],
        'dias': [row['total_dias'] or 0 for row in data],
        'casos': [row['casos'] for row in data],
    })


def api_top_pacientes(request):
    qs = _apply_filters(DescansoMedico.objects.all(), request)
    data = (
        qs.values('paciente__codigo', 'paciente__nombre')
        .annotate(casos=Count('id'), total_dias=Sum('dias'))
        .order_by('-casos', '-total_dias')[:20]
    )
    return JsonResponse({
        'labels': [f"{row['paciente__codigo']} - {row['paciente__nombre']}" for row in data],
        'casos': [row['casos'] for row in data],
        'dias': [row['total_dias'] or 0 for row in data],
    })
