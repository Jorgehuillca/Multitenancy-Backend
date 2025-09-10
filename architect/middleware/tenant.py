"""
Middleware para manejar multi-tenancy basado en el usuario autenticado.
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from architect.utils.tenant import get_tenant
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que agrega información del tenant a la request.
    """
    
    def process_request(self, request):
        """
        Agrega el tenant_id del usuario autenticado a la request.
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            tenant_id = get_tenant(request.user)
            request.tenant_id = tenant_id
            
            if tenant_id is None:
                logger.warning(
                    f"Usuario autenticado {request.user.id} no tiene tenant asignado"
                )
        else:
            request.tenant_id = None
            
        return None
