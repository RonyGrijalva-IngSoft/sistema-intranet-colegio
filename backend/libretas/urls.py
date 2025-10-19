from django.urls import path
from .api.views import BimestralPDFView, PdfPingView

urlpatterns = [
    path("bimestral/pdf", BimestralPDFView.as_view()),
    path("ping", PdfPingView.as_view()),
]
