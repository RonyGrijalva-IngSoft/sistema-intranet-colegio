from rest_framework import serializers
from .models import UGELDelegation, PasswordResetMock
from django.contrib.auth import get_user_model

User = get_user_model()


class UGELDelegationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UGELDelegation
        fields = ['id', 'tutor', 'delegated_by', 'active', 'created_at', 'expires_at']
        read_only_fields = ['delegated_by', 'created_at']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=8)
