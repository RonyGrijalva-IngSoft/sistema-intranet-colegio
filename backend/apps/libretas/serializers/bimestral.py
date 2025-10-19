# backend/apps/libretas/serializers/bimestral.py
from rest_framework import serializers

class BimestralPdfIn(serializers.Serializer):
    nivel = serializers.ChoiceField(choices=["Inicial", "Primaria", "Secundaria"])
    grado = serializers.CharField(max_length=50, required=False, allow_blank=True)
    seccion = serializers.IntegerField()
    curso = serializers.IntegerField(required=False, allow_null=True)
    bimestre = serializers.ChoiceField(choices=["B1", "B2", "B3", "B4"])
    descargaMasiva = serializers.BooleanField(default=False)
