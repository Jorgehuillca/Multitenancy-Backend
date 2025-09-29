from django.db import models
from django.utils import timezone

class ActiveMedicalRecordManager(models.Manager):
    """Manager por defecto que excluye registros soft-deleted."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class MedicalRecord(models.Model):
    """
    Historial médico que relaciona pacientes con diagnósticos.
    Basado en la estructura de la tabla medical_records de la BD.
    """

    #Multitenant
    reflexo = models.ForeignKey(
        'reflexo.Reflexo', 
        on_delete=models.CASCADE, 
        related_name='+',
        null=True,      # permite que sea vacío temporalmente
        blank=True      # permite que el formulario del admin lo deje vacío
    )
    
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, verbose_name="Paciente")
    diagnose = models.ForeignKey('Diagnosis', on_delete=models.CASCADE, verbose_name="Diagnóstico")
    
    # Información del diagnóstico
    diagnosis_date = models.DateField(verbose_name="Fecha de diagnóstico")
    symptoms = models.TextField(blank=True, null=True, verbose_name="Síntomas")
    treatment = models.TextField(blank=True, null=True, verbose_name="Tratamiento")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    
    # Estado del diagnóstico
    status = models.CharField(max_length=20, default='active', verbose_name="Estado")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")
    
    # Managers
    objects = ActiveMedicalRecordManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = 'Historial Médico'
        verbose_name_plural = 'Historiales Médicos'
        ordering = ['-diagnosis_date', '-created_at']
        # Permite múltiples registros para el mismo paciente/diagnóstico en fechas distintas
        unique_together = ['patient', 'diagnose', 'diagnosis_date']
    
    def soft_delete(self):
        """Soft delete del historial médico."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])
    
    def restore(self):
        """Restaura un historial médico eliminado."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])
    
    def __str__(self):
        return f"{self.patient} - {self.diagnose} ({self.diagnosis_date})"

    def clean(self):
        """Alinear tenant con el paciente y validar coherencia multitenant."""
        from django.core.exceptions import ValidationError

        if self.patient_id is None:
            return

        patient_reflexo_id = getattr(self.patient, 'reflexo_id', None)

        # Autocompletar tenant desde el paciente si falta
        if self.reflexo_id is None and patient_reflexo_id is not None:
            self.reflexo_id = patient_reflexo_id

        # Si ambos existen, deben coincidir
        if self.reflexo_id is not None and patient_reflexo_id is not None and self.reflexo_id != patient_reflexo_id:
            raise ValidationError({'reflexo': 'El historial debe pertenecer al mismo tenant que el paciente.'})

    def save(self, *args, **kwargs):
        # Garantizar validaciones siempre (Admin y API)
        self.full_clean()
        return super().save(*args, **kwargs)