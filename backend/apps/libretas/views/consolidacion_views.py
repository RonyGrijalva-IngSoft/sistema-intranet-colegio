# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from models import ConsolidadoBimestral, ConsolidadoUGEL
from services import ConsolidacionService
from dtos import ConsolidadoBimestralDTO, ConsolidadoUGELDTO
from serializers import *

class ConsolidadoBimestralViewSet(viewsets.ModelViewSet):
    queryset = ConsolidadoBimestral.objects.all()
    serializer_class = ConsolidadoBimestralSerializer
    
    @action(detail=False, methods=['post'])
    def consolidar(self, request):
        """Consolida un bimestre específico"""
        alumno_id = request.data.get('alumno_id')
        curso_id = request.data.get('curso_id')
        bimestre_id = request.data.get('bimestre_id')
        
        if not all([alumno_id, curso_id, bimestre_id]):
            return Response(
                {'error': 'Se requieren alumno_id, curso_id y bimestre_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            consolidado_dto = ConsolidacionService.consolidar_bimestre(
                alumno_id, curso_id, bimestre_id
            )
            
            # Convertir DTO a formato de respuesta
            response_data = {
                'id': consolidado_dto.id,
                'alumno_id': consolidado_dto.alumno_id,
                'alumno_nombre': consolidado_dto.alumno_nombre,
                'curso_id': consolidado_dto.curso_id,
                'curso_nombre': consolidado_dto.curso_nombre,
                'bimestre_id': consolidado_dto.bimestre_id,
                'bimestre_nombre': consolidado_dto.bimestre_nombre,
                'promedio_mensual_1': float(consolidado_dto.promedio_mensual_1) if consolidado_dto.promedio_mensual_1 else None,
                'promedio_mensual_2': float(consolidado_dto.promedio_mensual_2) if consolidado_dto.promedio_mensual_2 else None,
                'examen_bimestral': float(consolidado_dto.examen_bimestral) if consolidado_dto.examen_bimestral else None,
                'promedio_final': float(consolidado_dto.promedio_final) if consolidado_dto.promedio_final else None,
                'cerrado': consolidado_dto.cerrado,
                'precondiciones_cumplidas': consolidado_dto.precondiciones_cumplidas,
                'errores': consolidado_dto.errores
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error en consolidación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def verificar_precondiciones(self, request):
        """Verifica precondiciones para consolidación"""
        alumno_id = request.query_params.get('alumno_id')
        curso_id = request.query_params.get('curso_id')
        bimestre_id = request.query_params.get('bimestre_id')
        
        if not all([alumno_id, curso_id, bimestre_id]):
            return Response(
                {'error': 'Se requieren alumno_id, curso_id y bimestre_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        precondiciones = ConsolidacionService.verificar_precondiciones_bimestre(
            alumno_id, curso_id, bimestre_id
        )
        
        return Response({
            'cumplida': precondiciones.cumplida,
            'mensaje': precondiciones.mensaje,
            'detalles': precondiciones.detalles
        })

class ConsolidadoUGELViewSet(viewsets.ModelViewSet):
    queryset = ConsolidadoUGEL.objects.all()
    serializer_class = ConsolidadoUGELSerializer
    
    @action(detail=False, methods=['post'])
    def consolidar(self, request):
        """Consolida reporte UGEL para alumno y curso"""
        alumno_id = request.data.get('alumno_id')
        curso_id = request.data.get('curso_id')
        
        if not all([alumno_id, curso_id]):
            return Response(
                {'error': 'Se requieren alumno_id y curso_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            consolidado_dto = ConsolidacionService.consolidar_ugel(alumno_id, curso_id)
            
            response_data = {
                'id': consolidado_dto.id,
                'alumno_id': consolidado_dto.alumno_id,
                'alumno_codigo': consolidado_dto.alumno_codigo,
                'alumno_nombre': consolidado_dto.alumno_nombre,
                'curso_id': consolidado_dto.curso_id,
                'curso_nombre': consolidado_dto.curso_nombre,
                'bimestre_1': float(consolidado_dto.bimestre_1) if consolidado_dto.bimestre_1 else None,
                'bimestre_2': float(consolidado_dto.bimestre_2) if consolidado_dto.bimestre_2 else None,
                'bimestre_3': float(consolidado_dto.bimestre_3) if consolidado_dto.bimestre_3 else None,
                'bimestre_4': float(consolidado_dto.bimestre_4) if consolidado_dto.bimestre_4 else None,
                'promedio_final': float(consolidado_dto.promedio_final),
                'letra': consolidado_dto.letra,
                'comentario': consolidado_dto.comentario,
                'bimestres_disponibles': consolidado_dto.bimestres_disponibles
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error en consolidación UGEL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def reporte_ugel(self, request):
        """Obtiene todos los consolidados UGEL para generar reporte"""
        curso_id = request.query_params.get('curso_id')
        
        queryset = self.get_queryset()
        if curso_id:
            queryset = queryset.filter(curso_id=curso_id)
        
        # Usar el servicio para asegurar datos actualizados
        consolidados_actualizados = []
        for consolidado in queryset:
            consolidado_dto = ConsolidacionService.consolidar_ugel(
                consolidado.alumno_id, 
                consolidado.curso_id
            )
            consolidados_actualizados.append(consolidado_dto)
        
        serializer = ConsolidadoUGELReportSerializer(consolidados_actualizados, many=True)
        return Response(serializer.data)