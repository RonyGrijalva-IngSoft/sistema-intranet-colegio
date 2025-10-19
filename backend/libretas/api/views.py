from rest_framework.views import APIView
from django.http import FileResponse
from .serializers import BimestralPdfIn
from ..services.pdf_bimestral import render_pdf

class BimestralPDFView(APIView):
    def post(self, request):
        ser = BimestralPdfIn(data=request.data)
        ser.is_valid(raise_exception=True)
        pdf_bytes, filename = render_pdf(**ser.validated_data)
        return FileResponse(
            pdf_bytes,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )
