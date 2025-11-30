from django.db import models
from django.contrib.auth.models import User # Usaremos el sistema de auth por defecto

# --- 1. GESTIÓN DE PERSONAS Y USUARIOS ---

class Profesor(models.Model):
    # Vinculamos con el usuario de Django para el Login
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    dni = models.CharField(unique=True, max_length=15)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    es_directora = models.BooleanField(default=False) # Para diferenciar permisos rápidos

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Padre(models.Model):
    dni = models.CharField(unique=True, max_length=15)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

# --- 2. ESTRUCTURA ACADÉMICA ---

class AnioAcademico(models.Model):
    anio = models.IntegerField(unique=True) # Ej: 2024
    activo = models.BooleanField(default=True)

    def __str__(self):
        return str(self.anio)

class Grado(models.Model):
    nombre = models.CharField(max_length=50) # Ej: "1er Grado", "5to Secundaria"
    nivel = models.CharField(max_length=50)  # Ej: "Primaria", "Secundaria"

    def __str__(self):
        return f"{self.nombre} - {self.nivel}"

class Aula(models.Model):
    """
    Equivalente a tu anterior 'GradoTrabajado'.
    Representa un salón físico/lógico: 1er Grado A - 2024
    """
    nombre_seccion = models.CharField(max_length=10) # Ej: "A", "B", "Única"
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    anio_academico = models.ForeignKey(AnioAcademico, on_delete=models.CASCADE)
    
    # EL TUTOR: Responsable de ver las libretas de esta aula
    tutor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, related_name='aulas_tutoradas')

    class Meta:
        unique_together = ('grado', 'nombre_seccion', 'anio_academico')

    def __str__(self):
        return f"{self.grado} '{self.nombre_seccion}' - {self.anio_academico}"

class Alumno(models.Model):
    dni = models.CharField(unique=True, max_length=15)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    # El alumno pertenece a un Aula actual
    aula_actual = models.ForeignKey(Aula, on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    padre = models.ForeignKey(Padre, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

# --- 3. CURSOS Y ASIGNACIONES ---

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100) # Ej: "Matemática", "Historia"
    area = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class Periodo(models.Model):
    nombre = models.CharField(max_length=50) # Ej: "Bimestre 1", "Trimestre 2"
    anio_academico = models.ForeignKey(AnioAcademico, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False) # Solo se pueden meter notas en el periodo activo

    def __str__(self):
        return self.nombre

class AsignacionCurso(models.Model):
    """
    Equivalente a 'AsignaturaTrabajada'.
    Aquí es donde un profesor dicta un curso en un aula específica.
    """
    ESTADOS_DOCENTE = [
        ('BORRADOR', 'Borrador (Editando)'),
        ('ENVIADO_TUTOR', 'Enviado al Tutor'),
        ('OBSERVADO', 'Observado (Corregir)'), # Por si el tutor lo rechaza
    ]

    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='cursos_asignados')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='carga_academica')
    
    # Control de Estado por Bimestre/Periodo
    # Nota: Simplificado. En un sistema real complejo esto podría ser una tabla aparte,
    # pero para este alcance, asumiremos que el estado es global del periodo activo o se maneja por logica.
    # Para hacerlo bien detallado por periodo:
    
    def __str__(self):
        return f"{self.asignatura} en {self.aula} ({self.profesor})"

class EstadoCursoPeriodo(models.Model):
    """
    Controla si el profesor ya envió las notas de 'Matemáticas' del 'Bimestre 1'.
    """
    asignacion = models.ForeignKey(AsignacionCurso, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=AsignacionCurso.ESTADOS_DOCENTE, default='BORRADOR')
    fecha_envio = models.DateTimeField(null=True, blank=True)

# --- 4. SISTEMA DE NOTAS (DINÁMICO) ---

class Evaluacion(models.Model):
    """
    Representa la COLUMNA en el registro de notas.
    El profesor crea estas instancias dinámicamente.
    Ej: "Examen Mensual", "Revisión de Cuaderno".
    """
    asignacion = models.ForeignKey(AsignacionCurso, on_delete=models.CASCADE, related_name='evaluaciones')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100) # El encabezado de la columna
    peso = models.IntegerField(default=1, help_text="Peso para promedio (ej: 1, 2, o porcentaje)")
    
    def __str__(self):
        return f"{self.nombre} ({self.asignacion})"

class Nota(models.Model):
    """
    Representa la CELDA en el registro de notas.
    El valor numérico de un alumno en una evaluación.
    """
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='notas')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=5, decimal_places=2) # Ej: 15.50

    class Meta:
        unique_together = ('evaluacion', 'alumno') # Un alumno solo tiene una nota por evaluación

# --- 5. LIBRETAS Y APROBACIÓN (TUTOR -> DIRECTORA) ---

class Libreta(models.Model):
    """
    Consolidado de notas de un alumno en un periodo.
    Es lo que revisa la Tutora y aprueba la Directora.
    """
    ESTADOS_LIBRETA = [
        ('PROCESO', 'En Proceso (Faltan notas)'),
        ('REVISION_TUTOR', 'En Revisión por Tutor'),
        ('ENVIADO_DIRECCION', 'Enviado a Dirección'),
        ('APROBADA', 'Aprobada y Visible'),
        ('RECHAZADA', 'Rechazada'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE) # Redundante pero útil para consultas rápidas
    
    estado = models.CharField(max_length=20, choices=ESTADOS_LIBRETA, default='PROCESO')
    observacion_tutor = models.TextField(blank=True, null=True) # Comentario del tutor en la libreta
    promedio_ponderado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Detalles por asignación: {"<asignacion_id>": {"promedio": 12.5, "enviado": true, "aprobado_por_tutor": false}}
    detalles = models.JSONField(default=dict, blank=True)

    def recompute_promedio(self):
        """Recalcula `promedio_ponderado` a partir de los valores almacenados en `detalles`."""
        vals = []
        for k, v in (self.detalles or {}).items():
            try:
                p = float(v.get('promedio'))
                vals.append(p)
            except Exception:
                continue
        if not vals:
            self.promedio_ponderado = None
        else:
            avg = sum(vals) / len(vals)
            # Guardamos con dos decimales
            from decimal import Decimal
            self.promedio_ponderado = Decimal(f"{avg:.2f}")
        self.save()

    class Meta:
        unique_together = ('alumno', 'periodo')