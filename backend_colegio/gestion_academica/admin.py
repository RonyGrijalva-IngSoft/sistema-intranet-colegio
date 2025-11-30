from django.contrib import admin
from .models import (
    Profesor, Padre, AnioAcademico, Grado, Aula, 
    Alumno, Asignatura, Periodo, AsignacionCurso, 
    Evaluacion, Nota, Libreta
)

# Esto permite administrar todo desde el panel
admin.site.register(Profesor)
admin.site.register(Padre)
admin.site.register(AnioAcademico)
admin.site.register(Grado)
admin.site.register(Aula)
admin.site.register(Alumno)
admin.site.register(Asignatura)
admin.site.register(Periodo)
admin.site.register(AsignacionCurso)
admin.site.register(Evaluacion)
admin.site.register(Nota)
admin.site.register(Libreta)