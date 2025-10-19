# === STUB DE DATOS (para no depender de BD aún) ===

ALUMNOS = [
    {"id": 1001, "apellidos": "García Pérez", "nombres": "Ana"},
    {"id": 1002, "apellidos": "Rojas Díaz", "nombres": "Luis"},
    {"id": 1003, "apellidos": "Soto León", "nombres": "María"},
]

# Por curso_id: 101 = Matemática, 102 = Comunicación (ejemplo)
# B1..B4 por alumno
NOTAS = {
    (1, 123, 101): {  # grado=1, seccion_id=123, curso_id=101
        1001: {"B1": 18, "B2": 17, "B3": 16, "B4": 18},
        1002: {"B1": 13, "B2": 14, "B3": 15, "B4": 14},
        1003: {"B1": 10, "B2": 12, "B3": 11, "B4": 12},
    },
    (1, 123, 102): {  # curso_id=102
        1001: {"B1": 19, "B2": 18, "B3": 18, "B4": 19},
        1002: {"B1": 12, "B2": 13, "B3": 14, "B4": 14},
        1003: {"B1": 11, "B2": 11, "B3": 12, "B4": 12},
    },
}

CURSOS = {
    101: "Matemática",
    102: "Comunicación",
}

def get_alumnos_por_seccion(seccion_id: int):
    # En real: SELECT * FROM alumno WHERE seccion_id = ...
    return ALUMNOS

def get_cursos_de_grado(grado: int):
    # En real: desde malla curricular/tabla de cursos por grado
    return [{"id": 101, "nombre": CURSOS[101]}, {"id": 102, "nombre": CURSOS[102]}]

def get_notas(grado: int, seccion_id: int, curso_id: int):
    # En real: SELECT por periodo y consolidación
    return NOTAS.get((grado, seccion_id, curso_id), {})

def get_nota_bimestre(notas_alumno: dict, bimestre: int) -> float:
    return float(notas_alumno.get(f"B{bimestre}", 0))
