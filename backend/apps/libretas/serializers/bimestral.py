# backend/apps/libretas/serializers/bimestral.py
from __future__ import annotations
from rest_framework import serializers

class BimestralPreviewIn(serializers.Serializer):
    seccion = serializers.CharField()
    curso = serializers.CharField()
    bimestre = serializers.IntegerField(min_value=1, max_value=4)
    verificar = serializers.BooleanField(required=False, default=False)
