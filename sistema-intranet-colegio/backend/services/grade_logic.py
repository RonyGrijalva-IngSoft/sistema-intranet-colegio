from decimal import Decimal

def convertir_a_letra(promedio_numerico: Decimal) -> str:
    """Convierte la nota numérica (0-20) a la equivalencia literal (AD, A, B, C)."""
    promedio = promedio_numerico.quantize(Decimal('0.01'))
    
    # Reglas de Negocio para la conversión (según lo acordado en el proyecto)
    if promedio >= 18:
        return "AD"  # Logro Destacado
    elif promedio >= 14:
        return "A"   # Logro Esperado
    elif promedio >= 11:
        return "B"   # En Proceso
    else:
        return "C"   # En Inicio

def calcular_promedio(notas_lista: list[Decimal]) -> Decimal:
    """Calcula el promedio de una lista de calificaciones."""
    if not notas_lista:
        return Decimal('0.00')
    # Suma y divide. Redondea a dos decimales.
    return Decimal(sum(notas_lista) / len(notas_lista)).quantize(Decimal('0.01'))