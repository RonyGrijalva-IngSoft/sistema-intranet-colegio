from rest_framework import serializers

class BimestralPdfIn(serializers.Serializer):
    nivel = serializers.ChoiceField(choices=["inicial", "primaria", "secundaria"])
    grado = serializers.IntegerField(min_value=1, max_value=6)
    seccion_id = serializers.IntegerField()
    bimestre = serializers.IntegerField(min_value=1, max_value=4)
    incluir_examen = serializers.BooleanField(default=True)
