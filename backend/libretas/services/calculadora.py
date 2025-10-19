def to_letra(promedio: float) -> str:
    # Ajusta rangos según reglamento del cole si cambia
    if promedio >= 18: return "AD"
    if promedio >= 14: return "A"
    if promedio >= 11: return "B"
    return "C"
