"""Normaliza headers de Excel y los mapea a campos del modelo.

El Excel oficial llega con columnas: Código, Nombre del Trabajador, Gerencia,
Fecha de Inicio DM, Fecha de Término DM, Dias DM, Clasificación, Observaciones.

Mantenemos alias por si la fuente cambia ligeramente (mayúsculas, tildes,
sinónimos comunes).
"""

import re
import unicodedata


def normalize(text: str) -> str:
    if text is None:
        return ''
    s = str(text).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'\s+', ' ', s)
    return s


FIELD_ALIASES = {
    'codigo': {
        'codigo', 'cod', 'cod paciente', 'codigo paciente', 'codigo trabajador',
        'cod trabajador', 'dni',
    },
    'nombre': {
        'nombre del trabajador', 'nombre trabajador', 'nombre', 'trabajador',
        'paciente', 'nombre paciente', 'nombres y apellidos',
    },
    'gerencia': {
        'gerencia', 'area', 'unidad', 'departamento',
    },
    'fecha_inicio': {
        'fecha de inicio dm', 'fecha inicio dm', 'fecha inicio', 'inicio dm',
        'fecha de inicio', 'fec inicio',
    },
    'fecha_fin': {
        'fecha de termino dm', 'fecha termino dm', 'fecha de termino',
        'fecha termino', 'fecha fin dm', 'fecha fin', 'fin dm', 'fec termino',
    },
    'dias': {
        'dias dm', 'dias', 'dias de descanso', 'cantidad de dias',
    },
    'motivo': {
        'clasificacion', 'clasificacion motivo', 'motivo', 'tipo', 'diagnostico',
    },
    'observaciones': {
        'observaciones', 'observacion', 'comentarios', 'comentario', 'detalle',
    },
}

REQUIRED_FIELDS = ['codigo', 'nombre', 'gerencia', 'fecha_inicio', 'fecha_fin', 'motivo']


def build_header_map(header_row: list[str]) -> tuple[dict[str, int], list[str]]:
    """Mapea cada campo lógico al índice de columna en el header.

    Devuelve (mapping, missing_required). Si todo va bien, missing_required es [].
    """
    normalized_headers = [normalize(h) for h in header_row]
    mapping: dict[str, int] = {}

    for field, aliases in FIELD_ALIASES.items():
        for idx, header in enumerate(normalized_headers):
            if header in aliases:
                mapping[field] = idx
                break

    missing = [f for f in REQUIRED_FIELDS if f not in mapping]
    return mapping, missing
