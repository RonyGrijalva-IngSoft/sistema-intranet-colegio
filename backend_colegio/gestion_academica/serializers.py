from rest_framework import serializers
import re
from django.contrib.auth.models import User
from .models import Profesor, Aula, Alumno, AsignacionCurso, Evaluacion, Nota, Grado, AnioAcademico, Asignatura, Periodo

class ProfesorSerializer(serializers.ModelSerializer):
    # Campo virtual para recibir la contraseña y crear el User
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Profesor
        # Exponemos los campos relevantes; `usuario` se muestra como read-only
        fields = ['id', 'dni', 'nombres', 'apellidos', 'correo', 'telefono', 'es_directora', 'usuario', 'password']
        read_only_fields = ['usuario']

    def create(self, validated_data):
        password = validated_data.pop('password')

        # Normalize text fields to UPPERCASE (except correo and password)
        if 'nombres' in validated_data and validated_data['nombres']:
            validated_data['nombres'] = validated_data['nombres'].upper()
        if 'apellidos' in validated_data and validated_data['apellidos']:
            validated_data['apellidos'] = validated_data['apellidos'].upper()
        if 'telefono' in validated_data and validated_data['telefono']:
            validated_data['telefono'] = str(validated_data['telefono']).upper()

        # Creamos el perfil de profesor
        profesor = Profesor.objects.create(**validated_data)

        # Crearemos un usuario de Django vinculado para permitir login
        username = validated_data.get('correo') or profesor.dni
        # Si ya existe un usuario con ese username, le añadimos un sufijo
        if User.objects.filter(username=username).exists():
            username = f"{username}-{profesor.id}"

        user = User.objects.create_user(username=username)
        user.set_password(password)
        # Rellenamos nombre y correo en User
        # Guardamos nombres en mayúsculas en el User también
        user.first_name = (profesor.nombres or '').upper()
        user.last_name = (profesor.apellidos or '').upper()
        if profesor.correo:
            user.email = profesor.correo
        user.save()

        profesor.usuario = user
        profesor.save()

        return profesor

    def validate(self, data):
        # nombres y apellidos no vacíos y sin números
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        dni = data.get('dni')
        # If updating partially, only validate provided fields
        is_update = getattr(self, 'instance', None) is not None
        if is_update:
            if 'nombres' in data:
                if not nombres or not str(nombres).strip():
                    raise serializers.ValidationError({'nombres': 'El nombre no puede estar vacío.'})
                if any(ch.isdigit() for ch in str(nombres)):
                    raise serializers.ValidationError({'nombres': 'El nombre no puede contener números.'})
            if 'apellidos' in data:
                if not apellidos or not str(apellidos).strip():
                    raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden estar vacíos.'})
                if any(ch.isdigit() for ch in str(apellidos)):
                    raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden contener números.'})
            if 'dni' in data:
                if dni is None or not re.fullmatch(r"\d{8}", str(dni)):
                    raise serializers.ValidationError({'dni': 'El DNI debe contener exactamente 8 dígitos.'})
            return data

        # Creation: require fields
        if not nombres or not str(nombres).strip():
            raise serializers.ValidationError({'nombres': 'El nombre no puede estar vacío.'})
        if any(ch.isdigit() for ch in str(nombres)):
            raise serializers.ValidationError({'nombres': 'El nombre no puede contener números.'})
        if not apellidos or not str(apellidos).strip():
            raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden estar vacíos.'})
        if any(ch.isdigit() for ch in str(apellidos)):
            raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden contener números.'})
        # validar DNI: exactamente 8 dígitos
        if dni is None:
            raise serializers.ValidationError({'dni': 'El DNI es requerido.'})
        if not re.fullmatch(r"\d{8}", str(dni)):
            raise serializers.ValidationError({'dni': 'El DNI debe contener exactamente 8 dígitos.'})
        return data

    def update(self, instance, validated_data):
        # Normalize text fields to UPPERCASE (except correo)
        if 'nombres' in validated_data and validated_data['nombres']:
            validated_data['nombres'] = validated_data['nombres'].upper()
        if 'apellidos' in validated_data and validated_data['apellidos']:
            validated_data['apellidos'] = validated_data['apellidos'].upper()
        if 'telefono' in validated_data and validated_data['telefono']:
            validated_data['telefono'] = str(validated_data['telefono']).upper()
        return super().update(instance, validated_data)

class AlumnoSerializer(serializers.ModelSerializer):
    aula_nombre = serializers.CharField(source='aula_actual.nombre_seccion', read_only=True)

    class Meta:
        model = Alumno
        fields = '__all__'

    def validate(self, data):
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        dni = data.get('dni')
        is_update = getattr(self, 'instance', None) is not None
        if is_update:
            if 'nombres' in data:
                if not nombres or not str(nombres).strip():
                    raise serializers.ValidationError({'nombres': 'El nombre no puede estar vacío.'})
                if any(ch.isdigit() for ch in str(nombres)):
                    raise serializers.ValidationError({'nombres': 'El nombre no puede contener números.'})
            if 'apellidos' in data:
                if not apellidos or not str(apellidos).strip():
                    raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden estar vacíos.'})
                if any(ch.isdigit() for ch in str(apellidos)):
                    raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden contener números.'})
            if 'dni' in data:
                if dni is None or not re.fullmatch(r"\d{8}", str(dni)):
                    raise serializers.ValidationError({'dni': 'El DNI debe contener exactamente 8 dígitos.'})
            return data

        # Creation: require fields
        if not nombres or not str(nombres).strip():
            raise serializers.ValidationError({'nombres': 'El nombre no puede estar vacío.'})
        if any(ch.isdigit() for ch in str(nombres)):
            raise serializers.ValidationError({'nombres': 'El nombre no puede contener números.'})
        if not apellidos or not str(apellidos).strip():
            raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden estar vacíos.'})
        if any(ch.isdigit() for ch in str(apellidos)):
            raise serializers.ValidationError({'apellidos': 'Los apellidos no pueden contener números.'})
        if dni is None:
            raise serializers.ValidationError({'dni': 'El DNI es requerido.'})
        if not re.fullmatch(r"\d{8}", str(dni)):
            raise serializers.ValidationError({'dni': 'El DNI debe contener exactamente 8 dígitos.'})
        return data

    def create(self, validated_data):
        # Uppercase text fields (except correo if present)
        if 'nombres' in validated_data and validated_data['nombres']:
            validated_data['nombres'] = validated_data['nombres'].upper()
        if 'apellidos' in validated_data and validated_data['apellidos']:
            validated_data['apellidos'] = validated_data['apellidos'].upper()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'nombres' in validated_data and validated_data['nombres']:
            validated_data['nombres'] = validated_data['nombres'].upper()
        if 'apellidos' in validated_data and validated_data['apellidos']:
            validated_data['apellidos'] = validated_data['apellidos'].upper()
        return super().update(instance, validated_data)

class AulaSerializer(serializers.ModelSerializer):
    grado_nombre = serializers.CharField(source='grado.nombre', read_only=True)
    tutor_nombre = serializers.CharField(source='tutor.__str__', read_only=True)

    class Meta:
        model = Aula
        fields = ['id', 'nombre_seccion', 'grado', 'grado_nombre', 'anio_academico', 'tutor', 'tutor_nombre']

class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = '__all__'

class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nota
        fields = '__all__'

# Este es clave para la tabla de notas del profesor
class AsignacionCursoSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='asignatura.nombre', read_only=True)
    aula_nombre = serializers.CharField(source='aula.nombre_seccion', read_only=True)
    grado = serializers.CharField(source='aula.grado.nombre', read_only=True)

    class Meta:
        model = AsignacionCurso
        fields = '__all__'


# Serializers sencillos para modelos básicos
class GradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = '__all__'


class AnioAcademicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnioAcademico
        fields = '__all__'


class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = '__all__'


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = '__all__'


class LibretaSerializer(serializers.ModelSerializer):
    alumno_nombre = serializers.CharField(source='alumno.__str__', read_only=True)
    aula_nombre = serializers.CharField(source='aula.nombre_seccion', read_only=True)
    periodo_nombre = serializers.CharField(source='periodo.nombre', read_only=True)

    class Meta:
        model = __import__('gestion_academica.models', fromlist=['Libreta']).Libreta
        fields = ['id', 'alumno', 'alumno_nombre', 'periodo', 'periodo_nombre', 'aula', 'aula_nombre', 'estado', 'observacion_tutor', 'promedio_ponderado', 'detalles']