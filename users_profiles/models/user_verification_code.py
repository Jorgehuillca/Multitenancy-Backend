# users_profiles/models/user_verification_code.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class UserVerificationCode(models.Model):
    # user_id es UNIQUE en la tabla → OneToOneField
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        db_column='user_id',
        related_name='verification_code',
        null=True,
        blank=True,
    )

    #Multitenant
    reflexo = models.ForeignKey(
        'reflexo.Reflexo', 
        on_delete=models.CASCADE, 
        related_name='+',
        null=True,      # permite que sea vacío temporalmente
        blank=True      # permite que el formulario del admin lo deje vacío
    )

    code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Código')
    expires_at = models.DateTimeField(default=timezone.now, verbose_name='Expira en')
    failed_attempts = models.IntegerField(default=0, verbose_name='Intentos fallidos')
    locked_until = models.DateTimeField(blank=True, null=True, verbose_name='Bloqueado hasta')
    verification_type = models.CharField(max_length=50, default='password_change', verbose_name='Tipo de verificación')
    is_used = models.BooleanField(default=False, verbose_name='Usado')
    target_email = models.EmailField(blank=True, null=True, verbose_name='Email objetivo')

    # En la BD son TIMESTAMP con default/ON UPDATE; no usar auto_* si managed=False
    # Para que Django pueda crear/actualizar estos campos al gestionar la tabla
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado en')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado en')

    class Meta:
        db_table = 'users_verification_code'
        managed = True  # permitir que Django gestione/cree la tabla
        verbose_name = 'Código de verificación de usuario'
        verbose_name_plural = 'Códigos de verificación de usuarios'
        ordering = ['-created_at']

    def __str__(self):
        username = getattr(self.user, "user_name", getattr(self.user, "email", str(self.user_id)))
        return f'Código {self.code} para {username}'

    # Helpers opcionales
    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_locked(self):
        return self.locked_until and timezone.now() < self.locked_until

    def increment_failed_attempts(self):
        self.failed_attempts = (self.failed_attempts or 0) + 1
        self.save(update_fields=['failed_attempts', 'updated_at'])

    def lock_temporarily(self, minutes=15):
        self.locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save(update_fields=['locked_until', 'updated_at'])

    def unlock(self):
        self.locked_until = None
        self.failed_attempts = 0
        self.save(update_fields=['locked_until', 'failed_attempts', 'updated_at'])

    # API helpers esperados por las vistas
    def can_attempt(self, max_attempts: int = 5):
        """Retorna True si puede intentar validar el código."""
        if self.is_locked():
            return False
        return (self.failed_attempts or 0) < max_attempts

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=['is_used', 'updated_at'])

    @classmethod
    def create_code(cls, user, verification_type: str = 'password_change', ttl_minutes: int = 10, target_email: str | None = None):
        """Crea o regenera un código de verificación para el usuario.
        Devuelve la instancia con `code` y `expires_at` actualizados.
        """
        from random import randint
        code = f"{randint(0, 999999):06d}"
        expires = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={
                'code': code,
                'expires_at': expires,
                'failed_attempts': 0,
                'locked_until': None,
                'verification_type': verification_type,
                'is_used': False,
                'reflexo': getattr(user, 'reflexo', None),
                'target_email': target_email,
            }
        )
        return obj
