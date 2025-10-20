# dtos.py
# tipo: objetos de transferencia de datos
# crea estructuras optimizadas para mover información entre capas, evitando enviar objetos complejos de base de datos directamente.
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
