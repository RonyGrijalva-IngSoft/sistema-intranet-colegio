# consolidacion_serializers
# Serializadores que convierten modelos y DTOs de consolidados a JSON para APIs REST,
# incluyendo campos relacionados como nombres de alumnos, cursos y bimestres.
from rest_framework import serializers
from ..models import ConsolidadoBimestral, ConsolidadoUGEL

class ConsolidadoBimestralSerializer(serializers.ModelSerializer):
    alumno_nombre = serializers.CharField(source='alumno.__str__', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    bimestre_nombre = serializers.CharField(source='bimestre.nombre', read_only=True)
    
    class Meta:
        model = ConsolidadoBimestral
        fields = '__all__'

class ConsolidadoUGELSerializer(serializers.ModelSerializer):
    alumno_nombre = serializers.CharField(source='alumno.__str__', read_only=True)
    alumno_codigo = serializers.CharField(source='alumno.codigo', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = ConsolidadoUGEL
        fields = '__all__'

# Serializer para reportes
class ConsolidadoUGELReportSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    alumno_id = serializers.IntegerField()
    alumno_codigo = serializers.CharField()
    alumno_nombre = serializers.CharField()
    curso_id = serializers.IntegerField()
    curso_nombre = serializers.CharField()
    bimestre_1 = serializers.DecimalField(max_digits=4, decimal_places=2, allow_null=True)
    bimestre_2 = serializers.DecimalField(max_digits=4, decimal_places=2, allow_null=True)
    bimestre_3 = serializers.DecimalField(max_digits=4, decimal_places=2, allow_null=True)
    bimestre_4 = serializers.DecimalField(max_digits=4, decimal_places=2, allow_null=True)
    promedio_final = serializers.DecimalField(max_digits=4, decimal_places=2)
    letra = serializers.CharField()
    comentario = serializers.CharField()
    bimestres_disponibles = serializers.IntegerField()