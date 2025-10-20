# backend/apps/libretas/services/calc_service.py
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

_TWO = Decimal("2")
_Q = Decimal("0.01")

def _to_dec(v: float | int | Decimal) -> Decimal:
    if v is None:
        raise TypeError("None no es permitido")
    return Decimal(str(v))

def _round2(value: Decimal | float | int) -> Decimal:
    return _to_dec(value).quantize(_Q, rounding=ROUND_HALF_UP)

def promedio_bimestral(prom_mensual: float, examen: float) -> float:
    """
    Regla 50–50 con redondeo a 2 decimales.
    """
    pm = _to_dec(prom_mensual)
    ex = _to_dec(examen)
    avg = (pm + ex) / _TWO
    return float(_round2(avg))

def promedio_parciales(*bims: Optional[float]) -> float:
    """
    Acepta 1–4 valores. Ignora None. Redondeo a 2 decimales.
    """
    vals = [_to_dec(v) for v in bims if v is not None]
    if not vals:
        return 0.0
    avg = sum(vals) / Decimal(len(vals))
    return float(_round2(avg))

def nota_a_letra(n: float | int | Decimal) -> str:
    """
    Conversión literal:
      <11.00 → C
      11.00..13.99 → B
      14.00..17.99 → A
      >=18.00 → AD
    """
    d = _round2(n)
    if d < Decimal("11.00"):
        return "C"
    if d < Decimal("14.00"):
        return "B"
    if d < Decimal("18.00"):
        return "A"
    return "AD"
