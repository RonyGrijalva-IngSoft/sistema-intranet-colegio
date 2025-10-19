# backend/apps/libretas/urls.py
from django.urls import path
from .views.pdf import BimestralPreviewView, BimestralPDFView
from .views.ugel import UgelExcelUploadView

urlpatterns = [
    # Libretas bimestrales (PDF)
    path("bimestral/preview", BimestralPreviewView.as_view(), name="bimestral-preview"),
    path("bimestral/pdf", BimestralPDFView.as_view(), name="bimestral-pdf"),

    # UGEL (Excel)
    path("ugel/upload", UgelExcelUploadView.as_view(), name="ugel-upload"),
    # Nota: consolidado/comentarios/export se agregan en S2.
]
