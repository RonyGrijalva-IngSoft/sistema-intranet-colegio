from io import BytesIO
from typing import Dict, Any, List
from django.template.loader import render_to_string
from weasyprint import HTML
from .calculadora import to_letra
from .comentarios import get_comentario
from .data_port import IDataPort

# Por ahora, el servicio requiere que le inyectes un adapter que implemente IDataPort.
# Puedes hacer eso en un "container" o dentro de la vista si prefieres.
# En esta rama w01, dejamos una función set_data_port() para inyectarlo desde settings o ready().
_DATA_PORT: IDataPort | None = None

def set_data_port(adapter: IDataPort):
    global _DATA_PORT
    _DATA_PORT = adapter

def _armar_filas(port: IDataPort, grado: int, seccion_id: int, bimestre: int) -> List[Dict[str, Any]]:
    alumnos = port.alumnos_por_seccion(seccion_id)
    cursos = port.cursos_de_grado(grado)
    filas: List[Dict[str, Any]] = []

    for cur in cursos:
        curso_id = cur["id"]
        nombre_curso = cur["nombre"]
        notas_curso = port.notas_de_curso(grado, seccion_id, curso_id)

        for alumno in alumnos:
            aid = alumno["id"]
            n = notas_curso.get(aid, {"B1":0,"B2":0,"B3":0,"B4":0})
            prom = round((n["B1"] + n["B2"] + n["B3"] + n["B4"]) / 4, 2) if any(n.values()) else 0.0
            letra = to_letra(prom) if prom > 0 else ""
            coment = get_comentario(grado, curso_id, letra) if letra else ""

            filas.append({
                "alumno": f'{alumno["apellidos"]}, {alumno["nombres"]}',
                "curso": nombre_curso,
                "B1": n["B1"], "B2": n["B2"], "B3": n["B3"], "B4": n["B4"],
                "prom": prom, "letra": letra, "coment": coment,
            })
    return filas

def render_pdf(nivel: str, grado: int, seccion_id: int, bimestre: int, incluir_examen: bool):
    if _DATA_PORT is None:
        raise RuntimeError("No hay DataPort configurado. Inyecta un adapter que implemente IDataPort.")
    filas = _armar_filas(_DATA_PORT, grado, seccion_id, bimestre)
    html = render_to_string(f"libretas/{nivel}_bimestre.html", {
        "nivel": nivel, "grado": grado, "seccion_id": seccion_id,
        "bimestre": bimestre, "filas": filas, "incluir_examen": incluir_examen
    })
    buf = BytesIO()
    HTML(string=html, base_url=".").write_pdf(buf)
    buf.seek(0)
    filename = f"{nivel.upper()}_{grado}_B{bimestre}.pdf"
    return buf, filename
