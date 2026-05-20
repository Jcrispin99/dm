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


def build_header_map(header_row) -> tuple[dict[str, int], list[str]]:
    """Mapea cada campo lógico al índice de columna en una fila dada.

    Devuelve (mapping, missing_required).
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


def find_header_in_sheet(rows, max_scan: int = 50) -> tuple[int, dict[str, int], list[str], list]:
    """Escanea las primeras filas para encontrar la cabecera real.

    Acepta el resultado de ws.iter_rows(values_only=True) o cualquier iterable
    de filas. La cabecera puede estar en cualquier posición (no necesariamente
    A1) — el Excel puede tener banners/títulos arriba o columnas vacías a la
    izquierda. Se elige la fila que contenga todos los campos obligatorios; si
    ninguna los tiene, devuelve la que tenga más coincidencias para que el
    mensaje de error sea útil.

    Devuelve (header_row_index_zero_based, mapping, missing, header_row_values).
    Si no se encontró ninguna fila con matches, header_row_index = -1.
    """
    best_idx = -1
    best_mapping: dict[str, int] = {}
    best_missing = list(REQUIRED_FIELDS)
    best_row: list = []

    for i, row in enumerate(rows):
        if i >= max_scan:
            break
        row_list = list(row) if row is not None else []
        mapping, missing = build_header_map(row_list)
        if not mapping:
            continue
        # preferimos filas que tienen todos los obligatorios; entre esas, la primera
        if not missing:
            return i, mapping, missing, row_list
        # si nadie tiene todos, guardamos la de mejor cobertura
        if len(mapping) > len(best_mapping):
            best_idx = i
            best_mapping = mapping
            best_missing = missing
            best_row = row_list

    return best_idx, best_mapping, best_missing, best_row
