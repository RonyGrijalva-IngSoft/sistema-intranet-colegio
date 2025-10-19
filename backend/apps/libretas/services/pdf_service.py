# backend/apps/libretas/services/pdf_service.py
from io import BytesIO
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from . import calc_service

def build_preview_dto(params: Dict[str, Any], filas):
    """
    Construye el DTO mínimo para vista previa/render PDF (S1).
    """
    nivel = params["nivel"]
    grado = params.get("grado") or ""
    seccion = params["seccion"]
    curso = params.get("curso")
    bimestre = params["bimestre"]
    colegio = "IEP Cristo Redentor de Nocheto"

    filas_out = []
    for f in filas:
        nota = calc_service.redondear_2(f["nota_num"])
        filas_out.append({
            "alumnoId": f["alumnoId"],
            "alumno": f["alumno"],
            "curso": str(curso) if curso else "Curso",
            "nota_num": nota,
            "nota_let": calc_service.num_a_letra(nota),
        })

    return {
        "cabecera": {
            "colegio": colegio,
            "nivel": nivel,
            "grado": grado,
            "seccion": seccion,
            "curso": curso,
            "bimestre": bimestre,
            "generado_en": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "filas": filas_out,
        "pie": {"folio": 1, "firma": "__________________"},
    }

def render_bimestral_pdf(dto: Dict[str, Any]) -> bytes:
    """
    Render "smoke" en PDF con ReportLab (S1).
    """
    buff = BytesIO()
    doc = SimpleDocTemplate(
        buff, pagesize=A4,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    c = dto["cabecera"]
    title = f"Libreta Bimestral - {c['nivel']} ({c['bimestre']})"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"{c['colegio']} - Grado: {c['grado']}  Sección: {c['seccion']}", styles["Normal"]))
    story.append(Paragraph(f"Curso: {c['curso']}  |  Generado: {c['generado_en']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    data = [["#", "Alumno", "Nota (Num)", "Nota (Letra)"]]
    for idx, f in enumerate(dto["filas"], start=1):
        data.append([idx, f["alumno"], f["nota_num"], f["nota_let"]])

    table = Table(data, repeatRows=1, colWidths=[25, 300, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    story.append(table)

    story.append(Spacer(1, 18))
    story.append(Paragraph(f"Firma y sello: {dto['pie']['firma']}", styles["Normal"]))
    doc.build(story)

    pdf = buff.getvalue()
    buff.close()
    return pdf
