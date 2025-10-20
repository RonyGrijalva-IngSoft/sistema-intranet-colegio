# models.py
# modelos de base de datos
# define la estructura de tablas donde se almacenan alumnos, cursos, notas bimestrales
# y consolidados, esuqleto de datos del sistema
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Bimestre(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)
   
    def __str__(self):
        return self.nombre


class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
   
    def __str__(self):
        return self.nombre


class Alumno(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=8)
   
    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"


class NotaMensual(models.Model):
    TIPOS_NOTA = [
        ('promedio_mensual_1', 'Promedio Mensual 1'),
        ('promedio_mensual_2', 'Promedio Mensual 2'),
        ('examen_bimestral', 'Examen Bimestral'),
    ]
   
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    bimestre = models.ForeignKey(Bimestre, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS_NOTA)
    valor = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    peso = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    descripcion = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        unique_together = ['alumno', 'curso', 'bimestre', 'tipo']


class ConsolidadoBimestral(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    bimestre = models.ForeignKey(Bimestre, on_delete=models.CASCADE)
    promedio_final = models.DecimalField(max_digits=4, decimal_places=2)
    cerrado = models.BooleanField(default=False)
   
    class Meta:
        unique_together = ['alumno', 'curso', 'bimestre']


class ConsolidadoUGEL(models.Model):
    LETRAS_EQUIVALENCIA = [
        ('AD', 'AD'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
   
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    bimestre_1 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    bimestre_2 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    bimestre_3 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    bimestre_4 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    promedio_final = models.DecimalField(max_digits=4, decimal_places=2)
    letra = models.CharField(max_length=2, choices=LETRAS_EQUIVALENCIA)
    comentario = models.TextField(blank=True)
   
    class Meta:
        unique_together = ['alumno', 'curso']
