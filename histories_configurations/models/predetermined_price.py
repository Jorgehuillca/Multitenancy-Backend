from django.db import models
from django.utils import timezone

class PredeterminedPrice(models.Model):
    """
    Modelo para gestionar los precios predeterminados.
    Basado en la estructura de la tabla predetermined_prices de la BD.
    """
    
    # Multitenant: cada precio predeterminado pertenece a un tenant (Reflexo)
    reflexo = models.ForeignKey(
        'reflexo.Reflexo',
        on_delete=models.CASCADE,
        related_name='+',
        null=True,
        blank=True,
        verbose_name='Empresa/Tenant'
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")

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
        return f"{self.name} - {self.price}"

    class Meta:
        db_table = "predetermined_prices"
        verbose_name = "Precio Predeterminado"
        verbose_name_plural = "Precios Predeterminados"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['reflexo', 'name'], name='uniq_predetermined_price_per_reflexo_name')
        ]
