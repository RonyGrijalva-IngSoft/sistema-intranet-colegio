# backend/apps/libretas/services/calc_service.py
from decimal import Decimal, ROUND_HALF_UP

def redondear_2(val):
    return float(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def num_a_letra(promedio):
    """
    Conversión simple (stub S1):
     - AD: >= 18
     - A : 14–17.99
     - B : 11–13.99
     - C : 0–10.99
    """
    p = float(promedio)
    if p >= 18:
        return "AD"
    if p >= 14:
        return "A"
    if p >= 11:
        return "B"
    return "C"
