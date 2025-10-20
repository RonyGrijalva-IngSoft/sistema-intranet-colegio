# backend/apps/libretas/views/ugel.py
from __future__ import annotations
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers.ugel import UgelConsolidadoIn, UgelExportIn
from ..services.ugel_service import construir_consolidado, exportar_excel, leer_base

class UgelConsolidadoView(APIView):
    """
    GET /libretas/ugel/consolidado?uploadId=..&grado=..&curso=..
    → [{alumnoId, alumno, curso, B1,B2,B3,B4, promedio, letra}]
    """
    def get(self, request):
        ser = UgelConsolidadoIn(data=request.query_params)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        out = construir_consolidado(
            upload_id=data["uploadId"],
            grado=data.get("grado") or "",
            curso=data.get("curso") or "",
        )
        return Response(out, status=status.HTTP_200_OK)

class UgelExportView(APIView):
    """
    POST /libretas/ugel/export
    Body: { uploadId, consolidado:[…], comentarios:[{alumnoId, texto}] }
    Resp: .xlsx con el mismo nombre (attachment) y misma estructura.
    """
    def post(self, request):
        ser = UgelExportIn(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        xbytes = exportar_excel(
            upload_id=data["uploadId"],
            consolidado=data["consolidado"],
            comentarios=data.get("comentarios") or [],
        )
        _path, fname, _sheets = leer_base(data["uploadId"])
        resp = HttpResponse(
            xbytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{fname}"'
        return resp
