from django.urls import path
from .views.ugel import UgelConsolidadoView, UgelExportView
from .views.pdf import BimestralPreviewView, BimestralPDFView

urlpatterns = [
    path("libretas/ugel/consolidado", UgelConsolidadoView.as_view()),
    path("libretas/ugel/export", UgelExportView.as_view()),
    path("libretas/bimestral/preview", BimestralPreviewView.as_view()),
    path("libretas/bimestral/pdf", BimestralPDFView.as_view()),
]
