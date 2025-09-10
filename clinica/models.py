from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clinica_profile',
        verbose_name='Usuario'
    )
    reflexo = models.ForeignKey(
        'reflexo.Reflexo',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Reflexo'
    )

    class Meta:
        db_table = 'clinica_user_profile'
        verbose_name = 'Perfil de Clínica'
        verbose_name_plural = 'Perfiles de Clínica'

    def __str__(self):
        if self.reflexo:
            return f"{self.user} ({self.reflexo})"
        return f"{self.user}"