from django.db import models
from django.db.models import DecimalField, PROTECT, SET_NULL

# NOTA: Se asume que los modelos base (Alumno, Curso, Profesor, Seccion)
# ya están definidos y disponibles en el ORM de Django para las ForeignKey.

# --- 1. Rubro: Define los rubros configurables (ej. Cuaderno, Tareas) ---
# Permite al Tutor configurar rubros.
class Rubro(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre

# --- 2. NotaMensual: Registro detallado de la calificación ---
# Almacena cada nota (0-20) con precisión de 2 decimales.
class NotaMensual(models.Model):
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)
    rubro = models.ForeignKey(Rubro, on_delete=PROTECT)
    
    # max_digits=4 (ej. 20.00), decimal_places=2 (para precisión)
    calificacion = DecimalField(max_digits=4, decimal_places=2) 
    mes = models.IntegerField()
    
    registrado_por = models.ForeignKey('Profesor', on_delete=SET_NULL, null=True) 
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Asegura que un alumno no tenga dos notas para el mismo rubro en el mismo curso/mes
        unique_together = ('alumno', 'curso', 'rubro', 'mes') 

# --- 3. ExamenBimestral: Nota separada para el cálculo 50-50 ---
# Registro separado del examen bimestral.
class ExamenBimestral(models.Model):
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)
    bimestre = models.IntegerField()
    
    # Nota del examen que usará la regla bimestral 50-50.
    calificacion = DecimalField(max_digits=4, decimal_places=2)
    
    class Meta:
        # Un alumno solo puede tener una nota de examen por curso y bimestre
        unique_together = ('alumno', 'curso', 'bimestre')

# --- 4. EstadoCierreMensual: Gestión del flujo de envío y bloqueo ---
# Controla el flujo de cierre de mes.
ESTADOS_CIERRE = (
    ('ABIERTO', 'Abierto'),
    ('REVISION', 'En Revisión'),
    ('CERRADO', 'Cerrado'), # Indica bloqueo de edición
)

class EstadoCierreMensual(models.Model):
    seccion = models.ForeignKey('Seccion', on_delete=models.CASCADE)
    mes = models.IntegerField()
    
    # Estados de flujo: Abierto, En Revisión, Cerrado (bloqueado)
    estado = models.CharField(max_length=10, choices=ESTADOS_CIERRE, default='ABIERTO') 
    
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Solo puede haber un estado de cierre por sección y mes
        unique_together = ('seccion', 'mes')