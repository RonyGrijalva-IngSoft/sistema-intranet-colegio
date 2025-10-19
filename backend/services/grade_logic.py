from decimal import Decimal, ROUND_HALF_UP

def calcular_promedio_mensual(notas: list[Decimal]) -> Decimal:
    """
    Calcula el promedio simple de una lista de notas del mes.
    El resultado se redondea a 2 decimales.
    """
    if not notas:
        return Decimal('0.00')

    suma_notas = sum(notas)
    promedio = suma_notas / Decimal(len(notas))
    # Redondeo a 2 decimales (al medio hacia arriba)
    return promedio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_promedio_bimestral(promedio_mensual: Decimal, examen_bimestral: Decimal) -> Decimal:
    """
    Aplica la Regla Bimestral 50-50: (Promedio Mensual + Examen Bimestral) / 2.
    El resultado se redondea a 2 decimales.
    """
    # Ambos promedios pesan 50%
    suma_total = promedio_mensual + examen_bimestral
    promedio_final = suma_total / Decimal(2)
    
    # Redondeo final a 2 decimales
    return promedio_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)