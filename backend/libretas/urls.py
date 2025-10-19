from django.urls import path
from .api.views import BimestralPDFView

urlpatterns = [
    path("bimestral/pdf", BimestralPDFView.as_view()),
]
