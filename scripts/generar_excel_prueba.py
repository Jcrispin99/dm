"""Genera un Excel de prueba con la estructura oficial:
Código, Nombre del Trabajador, Gerencia, Fecha de Inicio DM, Fecha de Término DM,
Dias DM, Clasificación, Observaciones.
"""

from datetime import date
from pathlib import Path

from openpyxl import Workbook

HEADERS = [
    'Código', 'Nombre del Trabajador', 'Gerencia',
    'Fecha de Inicio DM', 'Fecha de Término DM', 'Dias DM',
    'Clasificación', 'Observaciones',
]

ROWS = [
    ['T001', 'Ana Pérez',     'Gerencia Operaciones', date(2026, 3, 1),  date(2026, 3, 3),  3, 'Enfermedad común', 'Reposo en casa'],
    ['T002', 'Luis Gómez',    'Gerencia Operaciones', date(2026, 3, 5),  date(2026, 3, 10), 6, 'Accidente laboral', ''],
    ['T003', 'María Salinas', 'Gerencia Comercial',   date(2026, 3, 7),  date(2026, 3, 7),  1, 'Enfermedad común', 'Migraña'],
    ['T001', 'Ana Pérez',     'Gerencia Operaciones', date(2026, 4, 2),  date(2026, 4, 4),  3, 'Maternidad', ''],
    ['T004', 'Carlos Ruiz',   'Gerencia Sistemas',    date(2026, 4, 10), date(2026, 4, 12), 3, 'Enfermedad común', ''],
    ['T002', 'Luis Gómez',    'Gerencia Operaciones', date(2026, 4, 20), date(2026, 4, 25), 6, 'Accidente común', ''],
    ['T005', 'Sofía Vargas',  'Gerencia Comercial',   date(2026, 5, 1),  date(2026, 5, 2),  2, 'Enfermedad común', ''],
    ['T003', 'María Salinas', 'Gerencia Comercial',   date(2026, 5, 5),  date(2026, 5, 9),  5, 'Enfermedad común', 'Gripe fuerte'],
    # Fila inválida intencional: fecha_fin < fecha_inicio
    ['T006', 'Pedro Quispe',  'Gerencia Sistemas',    date(2026, 5, 10), date(2026, 5, 8),  1, 'Enfermedad común', 'fila a propósito mal'],
    # Fila inválida intencional: gerencia vacía
    ['T007', 'Rosa Cruz',     '',                     date(2026, 5, 11), date(2026, 5, 12), 2, 'Enfermedad común', ''],
]


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = 'Descansos'
    ws.append(HEADERS)
    for row in ROWS:
        ws.append(row)
    out = Path(__file__).resolve().parent.parent / 'sample.xlsx'
    wb.save(out)
    print(f'Excel de prueba generado en: {out}')


if __name__ == '__main__':
    main()
