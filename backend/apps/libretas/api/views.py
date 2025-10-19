from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import BimestralPdfIn
from ..services.pdf_bimestral import render_pdf
import traceback

class BimestralPDFView(APIView):
    def post(self, request):
        ser = BimestralPdfIn(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            pdf_bytes, filename = render_pdf(**ser.validated_data)
            pdf_bytes.seek(0)
            data = pdf_bytes.getvalue()
            resp = HttpResponse(data, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            resp["Content-Length"] = str(len(data))
            return resp
        except Exception as e:
            tb = traceback.format_exc()
            return HttpResponse(
                f"ERROR al generar PDF:\n{e}\n\nTRACEBACK:\n{tb}",
                status=500,
                content_type="text/plain; charset=utf-8",
            )

# ---------- PING DE PRUEBA ----------
from reportlab.pdfgen import canvas
from io import BytesIO

class PdfPingView(APIView):
    def get(self, request):
        buf = BytesIO()
        c = canvas.Canvas(buf)
        c.drawString(100, 750, "PDF OK")
        c.showPage()
        c.save()
        buf.seek(0)
        data = buf.getvalue()
        resp = HttpResponse(data, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="ping.pdf"'
        resp["Content-Length"] = str(len(data))
        return resp
