from django.contrib.auth.models import Group


def get_user_role(user):
    """
    Intentar obtener rol del usuario de forma flexible:
    - user.role
    - user.profile.role
    - primer group de Django
    """
    if not user or user.is_anonymous:
        return None
    role = getattr(user, 'role', None)
    if role:
        return role
    profile = getattr(user, 'profile', None)
    if profile:
        role = getattr(profile, 'role', None)
        if role:
            return role
    groups = user.groups.all()
    if groups.exists():
        return groups.first().name
    return None
