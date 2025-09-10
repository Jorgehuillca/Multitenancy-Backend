from django.db import models
from .province import Province

class District(models.Model):
    """
    Modelo para gestionar los distritos.
    Basado en la estructura de la tabla districts de la BD.
    """

    ubigeo_code = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código ubigeo"
    )
    # Secuencia visual 1..1874
    sequence = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="N°"
    )
    name = models.CharField(max_length=255, verbose_name="Nombre")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name="Provincia")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de eliminación")

    class Meta:
        db_table = 'districts'
        verbose_name = "Distrito"
        verbose_name_plural = "Distritos"
        ordering = ["sequence", "province__region__ubigeo_code", "province__ubigeo_code", "ubigeo_code", "name"]
        # Global (no multitenant constraint)

    def __str__(self):
        return f"{self.name} ({self.province.name})"
