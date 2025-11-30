from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gestion_academica import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()

# --- RUTAS CON BASENAME (OBLIGATORIO AL USAR GET_QUERYSET) ---
router.register(r'profesores', views.ProfesorViewSet, basename='profesor')
router.register(r'alumnos', views.AlumnoViewSet, basename='alumno')
router.register(r'aulas', views.AulaViewSet, basename='aula')
router.register(r'cursos-asignados', views.AsignacionCursoViewSet, basename='asignacioncurso')
router.register(r'evaluaciones', views.EvaluacionViewSet, basename='evaluacion') # <--- Aquí fallaba
router.register(r'notas', views.NotaViewSet, basename='nota')
router.register(r'grados', views.GradoViewSet, basename='grado')
router.register(r'anios', views.AnioViewSet, basename='anio')
router.register(r'asignaturas', views.AsignaturaViewSet, basename='asignatura')             # <--- Y aquí
router.register(r'periodos', views.PeriodoViewSet, basename='periodo')
router.register(r'libretas', views.LibretaViewSet, basename='libreta')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Rutas de Autenticación
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Ruta de Info de Usuario (Rol)
    path('api/user-info/', views.user_info, name='user_info'),
]