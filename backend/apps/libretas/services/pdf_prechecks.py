# backend/apps/libretas/services/pdf_prechecks.py
from __future__ import annotations

def verificar_cierre_bimestre(seccion: str, bimestre: int) -> bool:
    """
    Placeholder S2: en real, consulta DB/estado; aquí solo valida rango.
    """
    return 1 <= int(bimestre) <= 4

def verificar_examen_bimestral(seccion: str, curso: str, bimestre: int) -> bool:
    """
    Placeholder S2: en real, verifica existencia de examen cargado.
    """
    return bool(curso and curso.strip())
