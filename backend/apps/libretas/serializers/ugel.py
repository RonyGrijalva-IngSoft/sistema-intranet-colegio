# backend/apps/libretas/serializers/ugel.py
from __future__ import annotations
from rest_framework import serializers

class UgelConsolidadoIn(serializers.Serializer):
    uploadId = serializers.CharField()
    grado = serializers.CharField(required=False, allow_blank=True, default="")
    curso = serializers.CharField(required=False, allow_blank=True, default="")

class UgelFilaSerializer(serializers.Serializer):
    alumnoId = serializers.CharField()
    alumno = serializers.CharField()
    curso = serializers.CharField(required=False, allow_blank=True)
    B1 = serializers.FloatField(required=False, allow_null=True)
    B2 = serializers.FloatField(required=False, allow_null=True)
    B3 = serializers.FloatField(required=False, allow_null=True)
    B4 = serializers.FloatField(required=False, allow_null=True)
    promedio = serializers.FloatField()
    letra = serializers.CharField()

class UgelComentarioSerializer(serializers.Serializer):
    alumnoId = serializers.CharField()
    texto = serializers.CharField(allow_blank=True)

class UgelExportIn(serializers.Serializer):
    uploadId = serializers.CharField()
    consolidado = UgelFilaSerializer(many=True)
    comentarios = UgelComentarioSerializer(many=True, required=False)
