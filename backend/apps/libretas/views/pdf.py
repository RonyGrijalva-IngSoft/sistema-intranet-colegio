# backend/apps/libretas/views/pdf.py
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..serializers.bimestral import BimestralPdfIn
from ..services import pdf_service
from ..services import excel_adapter
from apps.accesos.permissions import RolePermission
from apps.accesos.models import AuditLog

class BimestralPreviewView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['Directora', 'Coordinador', 'Tutor', 'Docente']

    def get(self, request):
        ser = BimestralPdfIn(data=request.query_params)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # S1: datos mínimos desde DataPort Excel “dummy”
        filas = excel_adapter.dataport.alumnos_por_seccion_y_curso(
            seccion_id=data["seccion"], curso_id=data.get("curso")
        )
        dto = pdf_service.build_preview_dto(data, filas)
        return JsonResponse(dto, status=200)

class BimestralPDFView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['Directora', 'Coordinador', 'Tutor', 'Docente']

    def post(self, request):
        ser = BimestralPdfIn(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        if data.get("descargaMasiva"):
            # S1: aún no implementado (S3). Devolvemos 400 controlado.
            return JsonResponse(
                {"detail": "descargaMasiva estará disponible en Semana 3"},
                status=400
            )

        filas = excel_adapter.dataport.alumnos_por_seccion_y_curso(
            seccion_id=data["seccion"], curso_id=data.get("curso")
        )
        dto = pdf_service.build_preview_dto(data, filas)
        pdf_bytes = pdf_service.render_bimestral_pdf(dto)

        filename = f"libreta_{data['nivel']}_sec{data['seccion']}_bim{data['bimestre']}.pdf"
        # Auditoría: registro de export
        try:
            AuditLog.objects.create(actor=request.user, action='export_pdf', target_type='Libreta', target_id=filename)
        except Exception:
            # no bloquear si falla auditoría
            pass
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
