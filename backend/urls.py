from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RubroViewSet, NotasViewSet, ExamenBimestralViewSet, CierreMesViewSet

router = DefaultRouter()

# POST /config-evaluacion/ (rubros)
router.register(r'config-evaluacion', RubroViewSet, basename='config-evaluacion') 

# POST/PUT /notas/ y POST /notas/enviar
router.register(r'notas', NotasViewSet, basename='notas') 

# POST /examen-bimestral/ y GET /examen-bimestral/calcular-final
router.register(r'examen-bimestral', ExamenBimestralViewSet, basename='examen-bimestral') 

# POST /cierre-mes/ (usa la acción personalizada 'cerrar')
# NOTA: Usamos el nombre 'cierre-mes' para simplificar la ruta, aunque la clase es CierreMesViewSet
router.register(r'cierre-mes', CierreMesViewSet, basename='cierre-mes')

urlpatterns = [
    # Mapea todas las rutas definidas por el router
    path('', include(router.urls)),
]