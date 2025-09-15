"""
Middleware para procesar JWT antes del TenantMiddleware.
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from architect.utils.tenant import get_tenant
import logging

logger = logging.getLogger(__name__)


class JWTTenantMiddleware(MiddlewareMixin):
    """
    Middleware que procesa JWT y agrega información del tenant a la request.
    """
    
    def process_request(self, request):
        """
        Procesa JWT y agrega el tenant_id del usuario autenticado a la request.
        """
        # Procesar autenticación JWT
        jwt_auth = JWTAuthentication()
        try:
            # Intentar autenticar con JWT
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                request.user = user
                request._jwt_token = token
                logger.debug(f"Usuario autenticado via JWT: {user.email}")
            else:
                # Si no hay JWT, mantener el usuario actual (puede ser AnonymousUser)
                pass
        except Exception as e:
            logger.warning(f"Error en autenticación JWT: {e}")
            # En caso de error, mantener el usuario actual
            pass
        
        # Agregar información del tenant
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

