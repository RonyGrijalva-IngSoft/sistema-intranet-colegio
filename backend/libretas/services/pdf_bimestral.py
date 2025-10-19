from io import BytesIO
# Quitamos import de Django templates y WeasyPrint
# Usaremos ReportLab para generar el PDF en Windows (más estable)

from .data_port import IDataPort
from .calculadora import to_letra
from .comentarios import get_comentario

# ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

_DATA_PORT = None  # type: IDataPort | None

def set_data_port(adapter):
    global _DATA_PORT
    _DATA_PORT = adapter

def _armar_filas(port, grado, seccion_id, bimestre):
    alumnos = port.alumnos_por_seccion(seccion_id)
    cursos = port.cursos_de_grado(grado)
    filas = []
    for cur in cursos:
        curso_id = cur["id"]
        nombre_curso = cur["nombre"]
        notas_curso = port.notas_de_curso(grado, seccion_id, curso_id)
        for alumno in alumnos:
            aid = alumno["id"]
            n = notas_curso.get(aid, {"B1":0,"B2":0,"B3":0,"B4":0})
            if n["B1"] or n["B2"] or n["B3"] or n["B4"]:
                prom = round((n["B1"]+n["B2"]+n["B3"]+n["B4"])/4, 2)
                letra = to_letra(prom)
                coment = get_comentario(grado, curso_id, letra)
            else:
                prom, letra, coment = 0.0, "", ""
            filas.append({
                "alumno": f'{alumno["apellidos"]}, {alumno["nombres"]}',
                "curso": nombre_curso,
                "B1": n["B1"], "B2": n["B2"], "B3": n["B3"], "B4": n["B4"],
                "prom": prom, "letra": letra, "coment": coment,
            })
    return filas

def render_pdf(nivel, grado, seccion_id, bimestre, incluir_examen):
    if _DATA_PORT is None:
        raise RuntimeError("No hay DataPort configurado.")

    filas = _armar_filas(_DATA_PORT, grado, seccion_id, bimestre)

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=48, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    titulo = Paragraph(
        f"Libreta Bimestral — {nivel.capitalize()} | Grado {grado} | Sección {seccion_id} | Bimestre {bimestre}",
        styles["Heading2"]
    )
    story.append(titulo)
    story.append(Spacer(1, 12))

    data = [["Alumno", "Curso", "B1", "B2", "B3", "B4", "Prom.", "Letra", "Coment."]]
    for f in filas:
        data.append([f["alumno"], f["curso"], f["B1"], f["B2"], f["B3"], f["B4"], f["prom"], f["letra"], f["coment"]])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e5e7eb")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("ALIGN", (2,1), (6,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tabla)

    doc.build(story)
    buf.seek(0)
    filename = f"{nivel.UPPER()}_{grado}_B{bimestre}.pdf"
    return buf, filename
