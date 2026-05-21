from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseNotAllowed
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from .admin_site import reporte_admin_site
from .forms import UploadExcelForm
from .models import DescansoMedico, Gerencia, Paciente, Seguimiento
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
    context = {
        **reporte_admin_site.each_context(request),
        'form': form, 'result': result,
        'title': 'Cargar Excel',
    }
    return render(request, 'descansos/upload.html', context)


def dashboard_view(request):
    gerencias = Gerencia.objects.order_by('nombre')
    first = DescansoMedico.objects.order_by('fecha_inicio').values_list('fecha_inicio', flat=True).first()
    last = DescansoMedico.objects.order_by('-fecha_fin').values_list('fecha_fin', flat=True).first()
    context = {
        **reporte_admin_site.each_context(request),
        'gerencias': gerencias,
        'fecha_min': first or date.today(),
        'fecha_max': last or date.today(),
        'title': 'Dashboard',
    }
    return render(request, 'descansos/dashboard.html', context)


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
        'codigos': [row['paciente__codigo'] for row in data],
        'labels': [f"{row['paciente__codigo']} - {row['paciente__nombre']}" for row in data],
        'casos': [row['casos'] for row in data],
        'dias': [row['total_dias'] or 0 for row in data],
    })


def pacientes_view(request):
    pacientes = Paciente.objects.all().order_by('nombre')
    codigo_preseleccion = request.GET.get('codigo', '')
    context = {
        **reporte_admin_site.each_context(request),
        'pacientes': pacientes,
        'codigo_preseleccion': codigo_preseleccion,
        'title': 'Pacientes',
    }
    return render(request, 'descansos/pacientes.html', context)


def api_paciente_detalle(request, codigo):
    paciente = get_object_or_404(Paciente, codigo=codigo)
    descansos_qs = (
        DescansoMedico.objects
        .filter(paciente=paciente)
        .select_related('gerencia', 'motivo')
        .order_by('-fecha_inicio')
    )

    resumen = descansos_qs.aggregate(
        total_descansos=Count('id'),
        total_dias=Sum('dias'),
    )
    primero = descansos_qs.order_by('fecha_inicio').values_list('fecha_inicio', flat=True).first()
    ultimo = descansos_qs.values_list('fecha_inicio', flat=True).first()
    gerencias = list(
        descansos_qs.order_by().values_list('gerencia__nombre', flat=True).distinct()
    )

    descansos = [
        {
            'fecha_inicio': d.fecha_inicio.isoformat(),
            'fecha_fin': d.fecha_fin.isoformat(),
            'dias': d.dias,
            'motivo': d.motivo.nombre,
            'gerencia': d.gerencia.nombre,
            'observaciones': d.observaciones,
        }
        for d in descansos_qs
    ]

    seguimientos_qs = paciente.seguimientos.select_related('usuario').all()
    seguimientos = [
        {
            'id': s.id,
            'fecha': s.fecha.isoformat(),
            'medio': s.medio,
            'medio_display': s.get_medio_display(),
            'estado': s.estado,
            'estado_display': s.get_estado_display(),
            'notas': s.notas,
            'proximo_contacto': s.proximo_contacto.isoformat() if s.proximo_contacto else None,
            'usuario': s.usuario.username if s.usuario else None,
        }
        for s in seguimientos_qs
    ]

    return JsonResponse({
        'paciente': {
            'codigo': paciente.codigo,
            'nombre': paciente.nombre,
            'telefono': paciente.telefono,
        },
        'resumen': {
            'total_descansos': resumen['total_descansos'] or 0,
            'total_dias': resumen['total_dias'] or 0,
            'primer_descanso': primero.isoformat() if primero else None,
            'ultimo_descanso': ultimo.isoformat() if ultimo else None,
            'gerencias': gerencias,
        },
        'descansos': descansos,
        'seguimientos': seguimientos,
        'choices': {
            'medio': [{'value': k, 'label': v} for k, v in Seguimiento.MEDIO_CHOICES],
            'estado': [{'value': k, 'label': v} for k, v in Seguimiento.ESTADO_CHOICES],
        },
    })


def api_seguimiento_crear(request, codigo):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    paciente = get_object_or_404(Paciente, codigo=codigo)

    medio = (request.POST.get('medio') or '').strip()
    estado = (request.POST.get('estado') or '').strip()
    notas = (request.POST.get('notas') or '').strip()
    fecha_str = (request.POST.get('fecha') or '').strip()
    proximo_str = (request.POST.get('proximo_contacto') or '').strip()

    medios_validos = {k for k, _ in Seguimiento.MEDIO_CHOICES}
    estados_validos = {k for k, _ in Seguimiento.ESTADO_CHOICES}

    errores = []
    if medio not in medios_validos:
        errores.append('medio inválido')
    if estado not in estados_validos:
        errores.append('estado inválido')

    fecha = parse_datetime(fecha_str) if fecha_str else None
    if fecha_str and not fecha:
        errores.append('fecha inválida')
    if fecha and timezone.is_naive(fecha):
        fecha = timezone.make_aware(fecha, timezone.get_current_timezone())

    proximo = parse_date(proximo_str) if proximo_str else None
    if proximo_str and not proximo:
        errores.append('próximo contacto inválido')

    if errores:
        return JsonResponse({'ok': False, 'errores': errores}, status=400)

    seg = Seguimiento.objects.create(
        paciente=paciente,
        fecha=fecha or timezone.now(),
        medio=medio,
        estado=estado,
        notas=notas,
        proximo_contacto=proximo,
        usuario=request.user if request.user.is_authenticated else None,
    )

    return JsonResponse({'ok': True, 'id': seg.id})
