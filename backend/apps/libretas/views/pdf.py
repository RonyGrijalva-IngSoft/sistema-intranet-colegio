# backend/apps/libretas/views/pdf.py
from __future__ import annotations
from typing import Any, Dict

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Si tienes WeasyPrint instalado, se usará PDF; si no, devuelve HTML.
try:
    from weasyprint import HTML
    _HAS_WEASY = True
except Exception:
    _HAS_WEASY = False

from ..services.pdf_prechecks import verificar_cierre_bimestre, verificar_examen_bimestral


class BimestralPreviewView(APIView):
    """
    GET /libretas/bimestral/preview?seccion=..&curso=..&bimestre=..[&verificar=true]
    Vista liviana para que el front marque ✓/⚠ (no genera PDF).
    """
    def get(self, request):
        q = request.query_params
        seccion = str(q.get("seccion", "") or "")
        curso = str(q.get("curso", "") or "")
        try:
            bimestre = int(q.get("bimestre", 1))
        except Exception:
            bimestre = 1
        solo_prechecks = str(q.get("verificar", "false")).lower() in ("1", "true", "yes")

        cierre_ok = verificar_cierre_bimestre(seccion, bimestre)
        examen_ok = verificar_examen_bimestral(seccion, curso, bimestre)

        if solo_prechecks:
            return Response({"prechecks": {"cierre": cierre_ok, "examen": examen_ok}}, status=status.HTTP_200_OK)

        dto = {
            "seccion": seccion,
            "curso": curso,
            "bimestre": bimestre,
            "items": [],
            "prechecks": {"cierre": cierre_ok, "examen": examen_ok},
        }
        return Response(dto, status=status.HTTP_200_OK)


class BimestralPDFView(APIView):
    """
    GET /libretas/bimestral/pdf?grado=..&bimestre=..[&nivel=..][&curso=..]
    Genera el PDF real eligiendo plantilla por nivel (inicial/primaria/secundaria).
    - Detección automática por 'grado':
        3,4,5 -> inicial
        1..6  -> primaria
        1S/1sec/1 secundaria -> secundaria
      Si llega ?nivel=.., se usa ese nivel explícitamente.
    """
    def get(self, request):
        q = request.query_params
        grado = str(q.get("grado", "") or "").strip()
        curso = str(q.get("curso", "") or "").strip()
        try:
            bimestre = int(q.get("bimestre", 1))
        except Exception:
            bimestre = 1
        nivel_param = str(q.get("nivel", "") or "").lower().strip()

        # 1) Prechecks (compat con helpers existentes que piden 'seccion' y 'curso').
        #    Usamos grado como 'seccion' para no romper el helper.
        if not verificar_cierre_bimestre(grado, bimestre):
            return Response({"code": "BIM_NO_CERRADO"}, status=status.HTTP_400_BAD_REQUEST)
        if not verificar_examen_bimestral(grado, curso, bimestre):
            return Response({"code": "EXAM_NO_CARGADO"}, status=status.HTTP_400_BAD_REQUEST)

        # 2) Detección de nivel
        if nivel_param:
            nivel = nivel_param
        else:
            if grado in {"3", "4", "5"}:
                nivel = "inicial"
            elif grado in {"1", "2", "3", "4", "5", "6"}:
                nivel = "primaria"
            elif grado.lower() in {"1s", "1sec", "1 secundaria"}:
                nivel = "secundaria"
            else:
                nivel = "primaria"

        # 3) Selección de plantilla
        if nivel == "inicial":
            template = "libretas/bimestral_inicial.html"
        elif nivel == "secundaria":
            template = "libretas/bimestral_secundaria.html"
        else:
            template = "libretas/bimestral_primaria.html"

        titulo = f"BOLETA DE NOTAS 2025 – EDUCACIÓN {nivel.upper()}"
        contexto: Dict[str, Any] = {
            "grado": grado,
            "bimestre": bimestre,
            "titulo": titulo,
            "alumno": {"apellidos_nombres": "Perez Huaman, Ana Sofia"},
            "tutora_nombre": "Miss Dina Torres",
        }

        html_resp = render(request, template, contexto)
        html_str = html_resp.content.decode("utf-8")

        if _HAS_WEASY:
            pdf_bytes = HTML(string=html_str, base_url=request.build_absolute_uri("/")).write_pdf()
            resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        else:
            resp = HttpResponse(html_str, content_type="text/html")

        resp["Content-Disposition"] = f'inline; filename="boleta_{nivel}_G{grado}_B{bimestre}.pdf"'
        return resp
