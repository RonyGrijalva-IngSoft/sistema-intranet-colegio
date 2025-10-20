from rest_framework.permissions import BasePermission
from .utils import get_user_role
from .models import UGELDelegation


class RolePermission(BasePermission):
    """
    Permite acceso solo si request.user tiene un rol dentro de view.allowed_roles (lista).
    Uso: en la view defina allowed_roles = ['Directora','Coordinador', ...]
    """
    def has_permission(self, request, view):
        allowed = getattr(view, 'allowed_roles', None)
        if not allowed:
            return True
        role = get_user_role(request.user)
        return role in allowed


class CanManageUGEL(BasePermission):
    """
    Directora puede siempre; tutor si existe delegación activa.
    """
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        if role == 'Directora':
            return True
        return UGELDelegation.objects.filter(tutor=request.user, active=True).exists()
