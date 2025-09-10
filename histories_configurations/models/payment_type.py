from django.db import models
from django.utils import timezone

class PaymentType(models.Model):
    """
    Modelo para gestionar los tipos de pago.
    Basado en la estructura de la tabla payment_types de la BD.
    """

    name = models.CharField(
        max_length=50,
        unique=False,
        verbose_name="Nombre"
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de eliminación")

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def __str__(self):
        return self.name

    class Meta:
        db_table = "payment_types"
        verbose_name = "Tipo de Pago"
        verbose_name_plural = "Tipos de Pago"
        ordering = ['name']
        # Global (no multitenant constraint)
