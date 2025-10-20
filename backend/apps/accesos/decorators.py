from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def ensure_not_closed(get_instance_fn):
    """
    Decorador para métodos de APIView que modifican entidades.
    get_instance_fn(view, request, *args, **kwargs) -> instancia con atributo 'closed'
    Si closed==True devuelve 409 Conflict.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            instance = get_instance_fn(view, request, *args, **kwargs)
            if instance is None:
                return func(view, request, *args, **kwargs)
            if getattr(instance, 'closed', False):
                return Response({'detail': 'La entidad ya está cerrada y no puede editarse.'}, status=status.HTTP_409_CONFLICT)
            return func(view, request, *args, **kwargs)
        return wrapper
    return decorator
