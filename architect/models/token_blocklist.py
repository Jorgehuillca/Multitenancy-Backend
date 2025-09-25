from django.db import models
from django.conf import settings


class TokenBlocklist(models.Model):
    """
    Registro de tokens revocados por JTI. Un token en esta tabla se considera inválido.
    """
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'architect_token_blocklist'
        indexes = [
            models.Index(fields=['jti']),
        ]

    def __str__(self):
        return f"Revoked token {self.jti} for user {self.user_id}"
