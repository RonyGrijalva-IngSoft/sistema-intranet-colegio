# urls.py
# tipo: configuracion de rutas
# mapea urls como /api/consolidacion a las vistas correspondientes 
from django.urls import path
from ..views.consolidacion_views import (
    ConsolidadoBimestralView,
    ConsolidadoUGELView,
    VerificarPrecondicionesView
)

urlpatterns = [
    path('consolidacion/bimestral/', ConsolidadoBimestralView.as_view(), name='consolidar_bimestre'),
    path('consolidacion/ugel/', ConsolidadoUGELView.as_view(), name='consolidar_ugel'),
    path('consolidacion/precondiciones/', VerificarPrecondicionesView.as_view(), name='verificar_precondiciones'),
]
