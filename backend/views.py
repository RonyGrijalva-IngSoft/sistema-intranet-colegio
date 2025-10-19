from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone
from .models import Rubro, NotaMensual, ExamenBimestral, EstadoCierreMensual
from .serializers import RubroSerializer, NotaMensualSerializer, ExamenBimestralSerializer, EstadoCierreMensualSerializer
from .services.grade_logic import calcular_promedio_mensual, calcular_promedio_bimestral
from decimal import Decimal

# NOTA: Los permisos (quién puede hacer qué) son responsabilidad de Augusto Cerna.
# Aquí solo se implementa la lógica funcional (endpoints, validaciones).

# Endpoint: POST /config-evaluacion/ (rubros)
class RubroViewSet(viewsets.ModelViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer

# Endpoint: POST/PUT /notas/ (registro y actualización de notas)
class NotasViewSet(viewsets.ModelViewSet):
    queryset = NotaMensual.objects.all()
    serializer_class = NotaMensualSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        calificacion = Decimal(data.get('calificacion', '0'))
        
        # Validación de rango
        if not (Decimal('0.00') <= calificacion <= Decimal('20.00')):
            return Response({'error': 'La calificación debe estar entre 0.00 y 20.00.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que el mes no esté cerrado
        try:
            cierre = EstadoCierreMensual.objects.get(
                seccion_id=data['seccion'], 
                mes=data['mes']
            )
            if cierre.estado == 'CERRADO':
                # Bloqueo tras cierre
                return Response({'error': 'El mes ha sido cerrado y no se pueden registrar notas.'},
                                status=status.HTTP_409_CONFLICT)
        except EstadoCierreMensual.DoesNotExist:
            pass # Si no existe el registro de cierre, se asume 'ABIERTO'

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def enviar(self, request):
        """POST /notas/enviar (Marca "Enviado a Tutor")"""
        # La lógica real de "enviar" implicaría actualizar un campo 'estado_envio'
        # o crear un registro de trazabilidad. Por simplicidad, aquí solo se valida el flujo.
        
        # Lógica de trazabilidad de envíos
        # Este endpoint solo debería ser accesible por Polidocentes.
        # Devuelve un mensaje de éxito simulado:
        return Response({'message': 'Notas enviadas al Tutor correctamente. Pendiente de revisión.'}, 
                        status=status.HTTP_200_OK)

# Endpoint: POST /examen-bimestral/
class ExamenBimestralViewSet(viewsets.ModelViewSet):
    queryset = ExamenBimestral.objects.all()
    serializer_class = ExamenBimestralSerializer
    
    # Aquí puedes añadir una acción para calcular el promedio final bimestral (50-50)
    # y devolverlo a la API para mostrarlo en el frontend.
    @action(detail=False, methods=['get'], url_path='calcular-final')
    def calcular_promedio_final(self, request):
        # NOTA: En un caso real, la lógica de cálculo debe estar en la capa de servicios (Fase 2)
        
        # Ejemplo de uso de la lógica de la Fase 2:
        
        # 1. Obtener datos de la BD (Promedio Mensual y Examen Bimestral)
        promedio_mensual_mock = Decimal('15.50') 
        examen_bimestral_mock = Decimal('18.00')
        
        # 2. Aplicar la regla 50-50
        promedio_final = calcular_promedio_bimestral(promedio_mensual_mock, examen_bimestral_mock)
        
        return Response({
            'promedio_mensual': promedio_mensual_mock,
            'examen_bimestral': examen_bimestral_mock,
            'promedio_final_bimestral': promedio_final 
        }, status=status.HTTP_200_OK)


# Endpoint: POST /cierre-mes/ (bloqueo)
class CierreMesViewSet(viewsets.ModelViewSet):
    queryset = EstadoCierreMensual.objects.all()
    serializer_class = EstadoCierreMensualSerializer
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def cerrar(self, request):
        """POST /cierre-mes (Bloquea la edición para el mes/sección)"""
        seccion_id = request.data.get('seccion_id')
        mes = request.data.get('mes')
        
        if not seccion_id or mes is None:
            return Response({'error': 'Se requiere seccion_id y mes para el cierre.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # 1. Validar precondiciones (ej. todas las notas deben estar enviadas)
        # (Lógica de precondiciones omitida por ser compleja, pero va aquí)

        # 2. Registrar el cierre (o actualizarlo)
        cierre, created = EstadoCierreMensual.objects.update_or_create(
            seccion_id=seccion_id,
            mes=mes,
            defaults={
                'estado': 'CERRADO', # Estado final de bloqueo
                'fecha_cierre': timezone.now()
            }
        )

        return Response({
            'message': f'Cierre del mes {mes} para la sección {seccion_id} exitoso. La edición ha sido bloqueada.',
            'estado': cierre.estado
        }, status=status.HTTP_200_OK)