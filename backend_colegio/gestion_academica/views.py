from rest_framework import viewsets
from .models import Profesor, Alumno, Aula, AsignacionCurso, Evaluacion, Nota, Grado, AnioAcademico, Asignatura, Periodo
from .serializers import (
    ProfesorSerializer, AlumnoSerializer, AulaSerializer, 
    AsignacionCursoSerializer, EvaluacionSerializer, NotaSerializer,
    GradoSerializer, AnioAcademicoSerializer, AsignaturaSerializer, PeriodoSerializer,
)
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Libreta
from .serializers import (
    ProfesorSerializer, AlumnoSerializer, AulaSerializer, 
    AsignacionCursoSerializer, EvaluacionSerializer, NotaSerializer,
    GradoSerializer, AnioAcademicoSerializer, AsignaturaSerializer, PeriodoSerializer,
    # LibretaSerializer imported dynamically below
)
from .serializers import LibretaSerializer

# ViewSets nos crean automáticamente las rutas de LEER, CREAR, ACTUALIZAR y BORRAR

class ProfesorViewSet(viewsets.ModelViewSet):
    # include related User to avoid extra queries when serializing
    # and add deterministic ordering to avoid UnorderedObjectListWarning when paginating
    queryset = Profesor.objects.select_related('usuario').all().order_by('id')
    serializer_class = ProfesorSerializer

class AulaViewSet(viewsets.ModelViewSet):
    # select_related to avoid N+1 when listing aulas (grado, anio_academico, tutor)
    queryset = Aula.objects.select_related('grado', 'anio_academico', 'tutor').all()
    serializer_class = AulaSerializer

class AsignacionCursoViewSet(viewsets.ModelViewSet):
    serializer_class = AsignacionCursoSerializer

    def get_queryset(self):
        # Obtenemos al usuario que está haciendo la petición (gracias al Token)
        user = self.request.user
        
        # Si es superusuario (Directora), ve todo
        if user.is_staff:
            return AsignacionCurso.objects.select_related('aula', 'asignatura', 'profesor').all()
        
        # Si es profesor, buscamos su perfil y filtramos
        try:
            # Asumimos que el usuario tiene un perfil de 'profesor' asociado
            # (definido en models.py con OneToOneField)
            return AsignacionCurso.objects.select_related('aula', 'asignatura', 'profesor').filter(profesor__usuario=user)
        except AttributeError:
            # Si el usuario no es profesor ni admin, no ve nada
            return AsignacionCurso.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enviar_promedios(self, request, pk=None):
        """El profesor envía los promedios de su asignación para un periodo.
        Calcula el promedio por alumno en la asignación (periodo opcional) y guarda en la Libreta.detalles.
        """
        try:
            asignacion = self.get_object()
        except Exception:
            return Response({'detail': 'Asignación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # Validar que el usuario sea el profesor a cargo o admin
        user = request.user
        if not (user.is_staff or (hasattr(asignacion.profesor, 'usuario') and asignacion.profesor.usuario == user)):
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        periodo_id = request.data.get('periodo')
        if not periodo_id:
            # intentar obtener periodo activo
            periodo_qs = Periodo.objects.filter(activo=True)
            if periodo_qs.exists():
                periodo = periodo_qs.first()
            else:
                return Response({'detail': 'No hay periodo especificado ni activo.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                periodo = Periodo.objects.get(id=periodo_id)
            except Periodo.DoesNotExist:
                return Response({'detail': 'Periodo no existe.'}, status=status.HTTP_400_BAD_REQUEST)

        # Para optimizar, traemos evaluaciones UNA vez y todas las notas relacionadas
        alumnos = list(asignacion.aula.estudiantes.all())
        resumen = []
        evaluaciones = list(Evaluacion.objects.filter(asignacion=asignacion, periodo=periodo))
        # detectar examen una sola vez
        examen = next((e for e in evaluaciones if (e.nombre or '').lower() == 'examen bimestral'), None)

        # Cargar todas las notas para las evaluaciones y alumnos en una sola consulta
        notas_qs = Nota.objects.filter(evaluacion__in=[e.id for e in evaluaciones], alumno__in=[a.id for a in alumnos]).select_related('evaluacion')
        notas_map = {(n.alumno_id, n.evaluacion_id): n for n in notas_qs}

        for alumno in alumnos:
            total = 0.0
            total_peso = 0.0
            for eva in evaluaciones:
                # Omitir la evaluación de examen cuando hagamos la media base
                if examen and eva.id == (examen.id if examen else None):
                    continue
                nota_obj = notas_map.get((alumno.id, eva.id))
                if nota_obj:
                    try:
                        valor = float(nota_obj.valor)
                    except Exception:
                        continue
                    peso = float(eva.peso or 1)
                    total += valor * peso
                    total_peso += peso

            promedio = None
            if total_peso > 0:
                promedio = round(total / total_peso, 2)

            # Si existe Examen Bimestral, combínalo con el promedio base (sin doble conteo)
            if examen:
                nota_ex = notas_map.get((alumno.id, examen.id))
                try:
                    if nota_ex:
                        nota_ex_val = float(nota_ex.valor)
                        if promedio is None:
                            promedio = round(nota_ex_val, 2)
                        else:
                            promedio = round((promedio + nota_ex_val) / 2, 2)
                except Exception:
                    pass

            # Obtener o crear libreta para alumno+periodo
            libreta, created = Libreta.objects.get_or_create(alumno=alumno, periodo=periodo, defaults={'aula': asignacion.aula})
            detalles = libreta.detalles or {}
            detalles[str(asignacion.id)] = {'promedio': promedio, 'enviado': True, 'aprobado_por_tutor': False}
            libreta.detalles = detalles
            libreta.estado = 'REVISION_TUTOR'
            libreta.aula = asignacion.aula

            # Recalcular promedio_ponderado sin llamar al helper para evitar doble save
            vals = []
            for k, v in (libreta.detalles or {}).items():
                try:
                    p = float(v.get('promedio'))
                    vals.append(p)
                except Exception:
                    continue
            if not vals:
                libreta.promedio_ponderado = None
            else:
                from decimal import Decimal
                avg = sum(vals) / len(vals)
                libreta.promedio_ponderado = Decimal(f"{avg:.2f}")

            libreta.save()
            resumen.append({'alumno': alumno.id, 'promedio': promedio})

        return Response({'detail': 'Promedios enviados al tutor.', 'resumen': resumen})

class EvaluacionViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluacionSerializer
    
    def get_queryset(self):
        # Permitir filtrar por curso: /api/evaluaciones/?curso=15
        curso_id = self.request.query_params.get('curso')
        if curso_id:
            return Evaluacion.objects.filter(asignacion_id=curso_id)
        return Evaluacion.objects.all()

class NotaViewSet(viewsets.ModelViewSet):
    serializer_class = NotaSerializer

    def get_queryset(self):
        # Permitir filtrar por curso para cargar la matriz completa
        curso_id = self.request.query_params.get('curso')
        if curso_id:
            return Nota.objects.filter(evaluacion__asignacion_id=curso_id)
        return Nota.objects.all()

class AlumnoViewSet(viewsets.ModelViewSet):
    serializer_class = AlumnoSerializer

    def get_queryset(self):
        # use select_related to include aula_actual and avoid extra DB hits when serializing
        queryset = Alumno.objects.select_related('aula_actual').all()
        # Permitir filtrar por aula: /api/alumnos/?aula=1
        aula_id = self.request.query_params.get('aula')
        if aula_id:
            queryset = queryset.filter(aula_actual_id=aula_id)
        return queryset
    
class GradoViewSet(viewsets.ModelViewSet):
    queryset = Grado.objects.all()
    serializer_class = GradoSerializer


class AnioViewSet(viewsets.ModelViewSet):
    queryset = AnioAcademico.objects.all()
    serializer_class = AnioAcademicoSerializer


class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer


class PeriodoViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodoSerializer

    def get_queryset(self):
        queryset = Periodo.objects.all()
        activo = self.request.query_params.get('activo')
        if activo is not None:
            # aceptar 'true'/'false' o '1'/'0'
            val = activo.lower()
            if val in ['true', '1', 'yes']:
                queryset = queryset.filter(activo=True)
            elif val in ['false', '0', 'no']:
                queryset = queryset.filter(activo=False)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_active(self, request, pk=None):
        """Marca este periodo como activo y desactiva los otros del mismo año en una transacción."""
        try:
            periodo = self.get_object()
        except Exception:
            return Response({'detail': 'Periodo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Solo usuarios staff deberían poder cambiar periodos (opcional)
        user = request.user
        if not user.is_staff:
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            # Activar seleccionado
            periodo.activo = True
            periodo.save()
            # Desactivar los demás del mismo año
            Periodo.objects.filter(anio_academico=periodo.anio_academico).exclude(pk=periodo.pk).update(activo=False)

        serializer = self.get_serializer(periodo)
        return Response(serializer.data)


class LibretaViewSet(viewsets.ModelViewSet):
    queryset = Libreta.objects.all()
    serializer_class = LibretaSerializer

    def get_queryset(self):
        queryset = Libreta.objects.all()
        alumno = self.request.query_params.get('alumno')
        aula = self.request.query_params.get('aula')
        periodo = self.request.query_params.get('periodo')
        if alumno:
            queryset = queryset.filter(alumno_id=alumno)
        if aula:
            queryset = queryset.filter(aula_id=aula)
        if periodo:
            queryset = queryset.filter(periodo_id=periodo)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def aprobar_por_tutor(self, request, pk=None):
        libreta = self.get_object()
        # Verificar que quien aprueba es el tutor de la aula
        user = request.user
        if not (user.is_staff or (libreta.aula.tutor and libreta.aula.tutor.usuario == user)):
            return Response({'detail': 'No autorizado para aprobar.'}, status=status.HTTP_403_FORBIDDEN)

        # Marcar todos los detalles como aprobados por tutor
        detalles = libreta.detalles or {}
        for k, v in detalles.items():
            v['aprobado_por_tutor'] = True
        libreta.detalles = detalles
        libreta.estado = 'ENVIADO_DIRECCION'
        libreta.save()
        libreta.recompute_promedio()
        return Response({'detail': 'Libreta aprobada por tutor y enviada a Dirección.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def aprobar_por_direccion(self, request, pk=None):
        libreta = self.get_object()
        user = request.user
        # Sólo staff (directora) puede aprobar final
        if not user.is_staff:
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        libreta.estado = 'APROBADA'
        libreta.save()
        return Response({'detail': 'Libreta aprobada por Dirección.'})
    
# --- VISTA EXTRA PARA IDENTIFICAR ROL ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Devuelve si el usuario es administrador o no"""
    # Intentar encontrar perfil de Profesor vinculado
    profesor = None
    profesor_id = None
    es_tutor = False
    try:
        profesor = Profesor.objects.get(usuario=request.user)
        profesor_id = profesor.id
        # Si tiene aulas tutoradas, es tutor
        es_tutor = profesor.aulas_tutoradas.exists()
    except Profesor.DoesNotExist:
        # Fallback: intentar encontrar profesor por correo o por DNI (username)
        try:
            if request.user.email:
                profesor = Profesor.objects.get(correo__iexact=request.user.email)
            else:
                profesor = Profesor.objects.get(dni=request.user.username)
            # Vinculamos el perfil al User actual para futuras consultas
            profesor.usuario = request.user
            profesor.save()
            profesor_id = profesor.id
            es_tutor = profesor.aulas_tutoradas.exists()
        except Profesor.DoesNotExist:
            profesor = None

    return Response({
        'username': request.user.username,
        'es_admin': request.user.is_staff, # True si es Directora
        'es_directora': request.user.is_staff,
        'nombre_completo': f"{request.user.first_name} {request.user.last_name}",
        'profesor_id': profesor_id,
        'es_tutor': es_tutor
    })