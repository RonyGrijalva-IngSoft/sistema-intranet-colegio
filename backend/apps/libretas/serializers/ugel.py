# backend/apps/libretas/serializers/ugel.py
from rest_framework import serializers

class UgelUploadIn(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, f):
        name = getattr(f, "name", "")
        if not name.lower().endswith(".xlsx"):
            raise serializers.ValidationError("El archivo debe ser .xlsx")
        if f.size > 15 * 1024 * 1024:  # 15MB
            raise serializers.ValidationError("Archivo demasiado grande (>15MB)")
        return f
