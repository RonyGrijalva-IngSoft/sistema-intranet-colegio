# dtos.py
# Objetos de transferencia de datos para estructurar información de notas y consolidados
# entre capas de la aplicación, facilitando el manejo y validación de promedios académicos.
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List

@dataclass
class ConsolidadoBimestralDTO:
    id: int
    alumno_id: int
    alumno_nombre: str
    curso_id: int
    curso_nombre: str
    bimestre_id: int
    bimestre_nombre: str
    promedio_mensual_1: Optional[Decimal]
    promedio_mensual_2: Optional[Decimal]
    examen_bimestral: Optional[Decimal]
    promedio_final: Optional[Decimal]
    cerrado: bool
    precondiciones_cumplidas: bool
    errores: List[str]

@dataclass
class ConsolidadoUGELDTO:
    id: int
    alumno_id: int
    alumno_codigo: str
    alumno_nombre: str
    curso_id: int
    curso_nombre: str
    bimestre_1: Optional[Decimal]
    bimestre_2: Optional[Decimal]
    bimestre_3: Optional[Decimal]
    bimestre_4: Optional[Decimal]
    promedio_final: Decimal
    letra: str
    comentario: str
    bimestres_disponibles: int

@dataclass
class PrecondicionDTO:
    cumplida: bool
    mensaje: str
    detalles: List[str]