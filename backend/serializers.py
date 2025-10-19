from rest_framework import serializers
from .models import Rubro, NotaMensual, ExamenBimestral, EstadoCierreMensual

# Asumimos que los modelos base (Alumno, Curso, Profesor, Seccion) tienen Serializers
# definidos en otra parte del proyecto (ej. core/serializers.py o base/serializers.py).

# --- 1. RubroSerializer ---
class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = '__all__'
        read_only_fields = ['id']

# --- 2. NotaMensualSerializer ---
class NotaMensualSerializer(serializers.ModelSerializer):
    # Se usa para recibir y registrar las calificaciones
    class Meta:
        model = NotaMensual
        fields = ['id', 'alumno', 'curso', 'rubro', 'calificacion', 'mes', 'registrado_por']
        # Validaciones de rango (0-20) y decimales se harán en la vista (views.py).

# --- 3. ExamenBimestralSerializer ---
class ExamenBimestralSerializer(serializers.ModelSerializer):
    # Se usa para recibir y registrar la nota del examen bimestral
    class Meta:
        model = ExamenBimestral
        fields = ['id', 'alumno', 'curso', 'bimestre', 'calificacion']

# --- 4. EstadoCierreMensualSerializer ---
class EstadoCierreMensualSerializer(serializers.ModelSerializer):
    # Se usa para cambiar el estado de un mes (ej. a 'REVISION' o 'CERRADO')
    class Meta:
        model = EstadoCierreMensual
        fields = ['id', 'seccion', 'mes', 'estado', 'fecha_cierre']
        read_only_fields = ['fecha_cierre'] # Se setea en la vista (views.py)