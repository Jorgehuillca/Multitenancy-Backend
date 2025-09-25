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

    # Identificador secuencial por empresa (no reemplaza el ID global)
    local_id = models.IntegerField(null=True, blank=True, verbose_name="ID local (por empresa)")
    
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

    def clean(self):
        """
        Impedir más de un historial ACTIVO (deleted_at IS NULL) por paciente.
        Se ejecuta desde save() y también puede ser llamada por formularios.
        """
        from django.core.exceptions import ValidationError
        if self.patient_id is None:
            return
        qs = History.active.filter(patient_id=self.patient_id).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'patient': 'Este paciente ya tiene un historial activo.'})

    def save(self, *args, **kwargs):
        # Garantizar validaciones siempre (Admin y API)
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "histories"
        verbose_name = "Historial"
        verbose_name_plural = "Historiales"
        ordering = ['reflexo_id', 'local_id', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['reflexo', 'local_id'],
                name='uniq_history_local_id_per_reflexo',
                condition=models.Q(local_id__isnull=False)
            ),
            # Evitar duplicados: un único historial activo por paciente
            models.UniqueConstraint(
                fields=['patient'],
                name='uniq_active_history_per_patient',
                condition=models.Q(deleted_at__isnull=True)
            ),
        ]
