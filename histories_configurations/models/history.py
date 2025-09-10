from django.db import models
from django.utils import timezone

class ActiveHistoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class History(models.Model):
    """
    Modelo para gestionar los historiales médicos.
    Basado en la estructura de la tabla histories de la BD.
    """
    #Multitenant
    reflexo = models.ForeignKey(
        'reflexo.Reflexo', 
        on_delete=models.CASCADE, 
        related_name='+',
        null=True,      # permite que sea vacío temporalmente
        blank=True      # permite que el formulario del admin lo deje vacío
    )
    
    # Relación con paciente
    patient = models.ForeignKey('patients_diagnoses.Patient', on_delete=models.CASCADE, verbose_name="Paciente")
    
    # Información médica
    testimony = models.BooleanField(default=True, verbose_name="Testimonio")
    private_observation = models.TextField(blank=True, null=True, verbose_name="Observación privada")
    observation = models.TextField(blank=True, null=True, verbose_name="Observación")
    height = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name="Altura")
    weight = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, verbose_name="Peso")
    last_weight = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, verbose_name="Último peso")
    
    # Información específica
    menstruation = models.BooleanField(default=True, verbose_name="Menstruación")
    diu_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de DIU")
    gestation = models.BooleanField(default=True, verbose_name="Gestación")

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de eliminación")

    objects = models.Manager()
    active = ActiveHistoryManager()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def __str__(self):
        return f"Historial de {self.patient}"

    class Meta:
        db_table = "histories"
        verbose_name = "Historial"
        verbose_name_plural = "Historiales"
        ordering = ['-created_at']
