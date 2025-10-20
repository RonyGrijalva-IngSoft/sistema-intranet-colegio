from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100, null=True, blank=True)
    target_id = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.actor} - {self.action}"


class UGELDelegation(models.Model):
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ugel_delegations')
    delegated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='delegations_made')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"UGEL Delegation: {self.tutor} active={self.active}"


class PasswordResetMock(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"PasswordResetMock {self.user} used={self.used}"


# Modelo demo para Periodos (Mes/Bimestre) - si ya tienes otro modelo puedes omitir/ajustar
class Period(models.Model):
    name = models.CharField(max_length=200)
    closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='periods_closed')
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Period {self.name} closed={self.closed}"
