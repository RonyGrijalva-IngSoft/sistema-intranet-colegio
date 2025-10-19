from io import BytesIO
from openpyxl import Workbook
from .data_access import get_alumnos_por_seccion, get_notas
from .calculadora import to_letra
from .comentarios import get_comentario

def export_ugel(periodo: str, seccion_id: int, curso_id: int, plantilla_filename: str = "UGEL_2025.xlsx"):
    # periodo = "B1" | "B2" | "B3" | "B4"
    alumnos = get_alumnos_por_seccion(seccion_id)
    # Asumimos grado=1 (ejemplo). Si recibes grado en request, úsalo aquí:
    grado = 1
    notas_curso = get_notas(grado, seccion_id, curso_id)

    wb = Workbook()
    ws = wb.active
    ws.title = "UGEL"

    ws.append(["ID Alumno","Apellidos y Nombres","B1","B2","B3","B4","Prom.","Letra","Coment."])

    for a in alumnos:
        aid = a["id"]
        n = notas_curso.get(aid, {"B1":0,"B2":0,"B3":0,"B4":0})
        prom = round((n["B1"]+n["B2"]+n["B3"]+n["B4"])/4, 2)
        letra = to_letra(prom)
        coment = get_comentario(grado, curso_id, letra)

        ws.append([
            aid,
            f'{a["apellidos"]}, {a["nombres"]}',
            n["B1"], n["B2"], n["B3"], n["B4"],
            prom, letra, coment
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf, plantilla_filename
