# consolidacion_views
# tipo: vista api
# define endpoints REST como /consolidar/ y /reporte-ugel/ que reciben peticiones HTTP y devuelven respuestas JSON.
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

# Importaciones relativas corregidas
try:
    from ..services.consolidacion_service import ConsolidacionService
    from ..serializers.consolidacion_serializers import (
        ConsolidadoBimestralSerializer,
        ConsolidadoUGELSerializer
    )
except ImportError:
    # Fallback para desarrollo
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from services.consolidacion_service import ConsolidacionService

@method_decorator(csrf_exempt, name='dispatch')
class ConsolidadoBimestralView(View):
    def post(self, request, *args, **kwargs):
        """Consolida un bimestre específico"""
        try:
            data = json.loads(request.body)
            alumno_id = data.get('alumno_id')
            curso_id = data.get('curso_id')
            bimestre_id = data.get('bimestre_id')
            
            if not all([alumno_id, curso_id, bimestre_id]):
                return JsonResponse(
                    {'error': 'Se requieren alumno_id, curso_id y bimestre_id'}, 
                    status=400
                )
            
            # Usar el servicio de consolidación
            resultado = ConsolidacionService.consolidar_bimestre(
                int(alumno_id), int(curso_id), int(bimestre_id)
            )
            
            if resultado.get('success'):
                return JsonResponse({
                    'success': True,
                    'data': resultado
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': resultado.get('errors', [])
                }, status=400)
            
        except Exception as e:
            return JsonResponse(
                {'error': f'Error en consolidación: {str(e)}'}, 
                status=500
            )

@method_decorator(csrf_exempt, name='dispatch')
class ConsolidadoUGELView(View):
    def post(self, request, *args, **kwargs):
        """Consolida reporte UGEL para alumno y curso"""
        try:
            data = json.loads(request.body)
            alumno_id = data.get('alumno_id')
            curso_id = data.get('curso_id')
            
            if not all([alumno_id, curso_id]):
                return JsonResponse(
                    {'error': 'Se requieren alumno_id y curso_id'}, 
                    status=400
                )
            
            resultado = ConsolidacionService.consolidar_ugel(
                int(alumno_id), int(curso_id)
            )
            
            if resultado.get('success'):
                return JsonResponse({
                    'success': True,
                    'data': resultado
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': resultado.get('errors', [])
                }, status=400)
            
        except Exception as e:
            return JsonResponse(
                {'error': f'Error en consolidación UGEL: {str(e)}'}, 
                status=500
            )

@method_decorator(csrf_exempt, name='dispatch')
class VerificarPrecondicionesView(View):
    def post(self, request, *args, **kwargs):
        """Verifica precondiciones para consolidación"""
        try:
            data = json.loads(request.body)
            alumno_id = data.get('alumno_id')
            curso_id = data.get('curso_id')
            bimestre_id = data.get('bimestre_id')
            
            if not all([alumno_id, curso_id, bimestre_id]):
                return JsonResponse(
                    {'error': 'Se requieren alumno_id, curso_id y bimestre_id'}, 
                    status=400
                )
            
            precondiciones = ConsolidacionService.verificar_precondiciones(
                int(alumno_id), int(curso_id), int(bimestre_id)
            )
            
            return JsonResponse({
                'cumplida': precondiciones['cumplida'],
                'mensaje': precondiciones['mensaje'],
                'detalles': precondiciones['detalles']
            })
            
        except Exception as e:
            return JsonResponse(
                {'error': f'Error verificando precondiciones: {str(e)}'}, 
                status=500
            )