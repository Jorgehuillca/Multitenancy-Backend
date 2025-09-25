from rest_framework import permissions
from ..utils.tenant import is_global_admin


class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para usuarios administradores
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_global_admin(request.user))


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para propietarios o solo lectura
    """
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permisos de escritura solo para el propietario
        return obj.user == request.user 