from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils.translation import gettext_lazy as _

try:
    from .models.token_blocklist import TokenBlocklist
except Exception:
    TokenBlocklist = None


class BlocklistJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT que respeta un blocklist de tokens revocados.
    Si el jti del token está registrado en TokenBlocklist, el token se considera inválido.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, validated_token = result
        # Si no hay modelo (antes de migrar), no bloquear
        if TokenBlocklist is None:
            return user, validated_token
        jti = validated_token.get('jti')
        if jti and TokenBlocklist.objects.filter(jti=jti).exists():
            raise InvalidToken(_("Token revocado. Inicie sesión nuevamente."))
        return user, validated_token
