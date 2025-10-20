# consolidacion_service
# tipo: servicio de logica
# contiene todas las reglas de calculo academico, promedios, equivalencias, validaciones.

from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Q
from models import NotaMensual, ConsolidadoBimestral, ConsolidadoUGEL, Bimestre
from models import NotaMensual, ConsolidadoBimestral, ConsolidadoUGEL, Bimestre, Alumno, Curso
from dtos import ConsolidadoBimestralDTO, ConsolidadoUGELDTO, PrecondicionDTO


class ConsolidacionService:
   
    @staticmethod
    def calcular_equivalencia_letra(promedio: Decimal) -> str:
        """
        Calcula la equivalencia literal según las reglas UGEL
        AD: 18-20, A: 14-17, B: 11-13, C: 0-10
        """
        if promedio >= 18:
            return 'AD'
        elif promedio >= 14:
            return 'A'
        elif promedio >= 11:
            return 'B'
        else:
            return 'C'
   
    @staticmethod
    def verificar_precondiciones_bimestre(alumno_id: int, curso_id: int, bimestre_id: int) -> PrecondicionDTO:
        """
        Verifica precondiciones para consolidar un bimestre
        """
        errores = []
        detalles = []
       
        # Verificar si existen notas mensuales
        notas_mensuales = NotaMensual.objects.filter(
            alumno_id=alumno_id,
            curso_id=curso_id,
            bimestre_id=bimestre_id,
            tipo__in=['promedio_mensual_1', 'promedio_mensual_2']
        )
       
        if not notas_mensuales.exists():
            errores.append("No existen notas mensuales registradas")
        else:
            detalles.append(f"Notas mensuales: {notas_mensuales.count()} registros")
       
        # Verificar examen bimestral
        examen_bimestral = NotaMensual.objects.filter(
            alumno_id=alumno_id,
            curso_id=curso_id,
            bimestre_id=bimestre_id,
            tipo='examen_bimestral'
        ).exists()
       
        if not examen_bimestral:
            errores.append("No existe examen bimestral registrado")
        else:
            detalles.append("Examen bimestral: Registrado")
       
        # Verificar si el bimestre está cerrado
        bimestre = Bimestre.objects.get(id=bimestre_id)
        if not bimestre.cerrado:
            errores.append("El bimestre no está cerrado")
        else:
            detalles.append("Bimestre: Cerrado")
       
        cumplida = len(errores) == 0
        mensaje = "Precondiciones cumplidas" if cumplida else "Faltan precondiciones"
       
        return PrecondicionDTO(
            cumplida=cumplida,
            mensaje=mensaje,
            detalles=detalles
        )
   
    @staticmethod
    def consolidar_bimestre(alumno_id: int, curso_id: int, bimestre_id: int) -> ConsolidadoBimestralDTO:
        """
        Consolida las notas de un bimestre específico
        """
        # Verificar precondiciones
        precondiciones = ConsolidacionService.verificar_precondiciones_bimestre(
            alumno_id, curso_id, bimestre_id
        )
       
        if not precondiciones.cumplida:
            # Retornar DTO con errores
            alumno = Alumno.objects.get(id=alumno_id)
            curso = Curso.objects.get(id=curso_id)
            bimestre = Bimestre.objects.get(id=bimestre_id)
           
            return ConsolidadoBimestralDTO(
                id=0,
                alumno_id=alumno_id,
                alumno_nombre=str(alumno),
                curso_id=curso_id,
                curso_nombre=curso.nombre,
                bimestre_id=bimestre_id,
                bimestre_nombre=bimestre.nombre,
                promedio_mensual_1=None,
                promedio_mensual_2=None,
                examen_bimestral=None,
                promedio_final=None,
                cerrado=False,
                precondiciones_cumplidas=False,
                errores=precondiciones.detalles
            )
       
        # Calcular promedios
        notas_mensuales_1 = NotaMensual.objects.filter(
            alumno_id=alumno_id,
            curso_id=curso_id,
            bimestre_id=bimestre_id,
            tipo='promedio_mensual_1'
        )
       
        notas_mensuales_2 = NotaMensual.objects.filter(
            alumno_id=alumno_id,
            curso_id=curso_id,
            bimestre_id=bimestre_id,
            tipo='promedio_mensual_2'
        )
       
        examen_bimestral = NotaMensual.objects.get(
            alumno_id=alumno_id,
            curso_id=curso_id,
            bimestre_id=bimestre_id,
            tipo='examen_bimestral'
        )
       
        # Calcular promedio mensual 1
        promedio_mensual_1 = ConsolidacionService._calcular_promedio_ponderado(notas_mensuales_1)
       
        # Calcular promedio mensual 2
        promedio_mensual_2 = ConsolidacionService._calcular_promedio_ponderado(notas_mensuales_2)
       
        # Calcular promedio final del bimestre (60% promedio mensual + 40% examen)
        promedio_mensual_total = (promedio_mensual_1 + promedio_mensual_2) / 2
        promedio_final = (promedio_mensual_total * Decimal('0.6')) + (examen_bimestral.valor * Decimal('0.4'))
        promedio_final = promedio_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
       
        # Crear o actualizar consolidado bimestral
        consolidado, created = ConsolidadoBimestral.objects.update_or_create(
            alumno_id=alumno_id,
            curso_id=curso_id,
            bimestre_id=bimestre_id,
            defaults={
                'promedio_final': promedio_final,
                'cerrado': True
            }
        )
       
        alumno = Alumno.objects.get(id=alumno_id)
        curso = Curso.objects.get(id=curso_id)
        bimestre = Bimestre.objects.get(id=bimestre_id)
       
        return ConsolidadoBimestralDTO(
            id=consolidado.id,
            alumno_id=alumno_id,
            alumno_nombre=str(alumno),
            curso_id=curso_id,
            curso_nombre=curso.nombre,
            bimestre_id=bimestre_id,
            bimestre_nombre=bimestre.nombre,
            promedio_mensual_1=promedio_mensual_1,
            promedio_mensual_2=promedio_mensual_2,
            examen_bimestral=examen_bimestral.valor,
            promedio_final=promedio_final,
            cerrado=True,
            precondiciones_cumplidas=True,
            errores=[]
        )
   
    @staticmethod
    def consolidar_ugel(alumno_id: int, curso_id: int) -> ConsolidadoUGELDTO:
        """
        Consolida las notas para el reporte UGEL según las reglas específicas
        """
        # Obtener todos los bimestres consolidados para este alumno y curso
        consolidados_bimestrales = ConsolidadoBimestral.objects.filter(
            alumno_id=alumno_id,
            curso_id=curso_id,
            cerrado=True
        ).select_related('bimestre').order_by('bimestre__fecha_inicio')
       
        bimestres_disponibles = consolidados_bimestrales.count()
       
        # Obtener notas por bimestre
        bimestre_1 = None
        bimestre_2 = None
        bimestre_3 = None
        bimestre_4 = None
       
        for i, consolidado in enumerate(consolidados_bimestrales):
            if i == 0:
                bimestre_1 = consolidado.promedio_final
            elif i == 1:
                bimestre_2 = consolidado.promedio_final
            elif i == 2:
                bimestre_3 = consolidado.promedio_final
            elif i == 3:
                bimestre_4 = consolidado.promedio_final
       
        # Calcular promedio final según reglas UGEL
        promedios = [b for b in [bimestre_1, bimestre_2, bimestre_3, bimestre_4] if b is not None]
       
        if not promedios:
            promedio_final = Decimal('0.00')
        else:
            promedio_final = sum(promedios) / len(promedios)
            promedio_final = promedio_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
       
        # Calcular equivalencia literal
        letra = ConsolidacionService.calcular_equivalencia_letra(promedio_final)
       
        # Generar comentario automático
        comentario = ConsolidacionService._generar_comentario(promedio_final, letra, bimestres_disponibles)
       
        # Crear o actualizar consolidado UGEL
        alumno = Alumno.objects.get(id=alumno_id)
        curso = Curso.objects.get(id=curso_id)
       
        consolidado_ugel, created = ConsolidadoUGEL.objects.update_or_create(
            alumno_id=alumno_id,
            curso_id=curso_id,
            defaults={
                'bimestre_1': bimestre_1,
                'bimestre_2': bimestre_2,
                'bimestre_3': bimestre_3,
                'bimestre_4': bimestre_4,
                'promedio_final': promedio_final,
                'letra': letra,
                'comentario': comentario
            }
        )
       
        return ConsolidadoUGELDTO(
            id=consolidado_ugel.id,
            alumno_id=alumno_id,
            alumno_codigo=alumno.codigo,
            alumno_nombre=str(alumno),
            curso_id=curso_id,
            curso_nombre=curso.nombre,
            bimestre_1=bimestre_1,
            bimestre_2=bimestre_2,
            bimestre_3=bimestre_3,
            bimestre_4=bimestre_4,
            promedio_final=promedio_final,
            letra=letra,
            comentario=comentario,
            bimestres_disponibles=bimestres_disponibles
        )
   
    @staticmethod
    def _calcular_promedio_ponderado(notas_queryset) -> Decimal:
        """Calcula promedio ponderado de un conjunto de notas"""
        if not notas_queryset.exists():
            return Decimal('0.00')
       
        suma_ponderada = Decimal('0.00')
        suma_pesos = Decimal('0.00')
       
        for nota in notas_queryset:
            suma_ponderada += nota.valor * nota.peso
            suma_pesos += nota.peso
       
        if suma_pesos == 0:
            return Decimal('0.00')
       
        promedio = suma_ponderada / suma_pesos
        return promedio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
   
    @staticmethod
    def _generar_comentario(promedio: Decimal, letra: str, bimestres_disponibles: int) -> str:
        """Genera comentario automático basado en el desempeño"""
        if letra == 'AD':
            return f"Excelente desempeño académico. Promedio {promedio} en {bimestres_disponibles} bimestre(s)."
        elif letra == 'A':
            return f"Buen desempeño académico. Promedio {promedio} en {bimestres_disponibles} bimestre(s)."
        elif letra == 'B':
            return f"Desempeño regular. Necesita mejorar. Promedio {promedio} en {bimestres_disponibles} bimestre(s)."
        else:
            return f"Desempeño insuficiente. Requiere apoyo. Promedio {promedio} en {bimestres_disponibles} bimestre(s)."
