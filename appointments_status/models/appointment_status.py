from django.db import models


class AppointmentStatus(models.Model):
    """
    Modelo para gestionar los estados de las citas médicas.
    Basado en la estructura del módulo Laravel 05_appointments_status.
    """
    
    #Multitenant
    reflexo = models.ForeignKey(
        'reflexo.Reflexo',
        on_delete=models.CASCADE, 
        related_name='+',
        null=True,      # permite que sea vacío temporalmente
        blank=True      # permite que el formulario del admin lo deje vacío
    )
    
    name = models.CharField(
        max_length=50,
        verbose_name="Nombre del estado"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción"
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de eliminación")
    
    class Meta:
        db_table = 'appointment_statuses'
        verbose_name = "Estado de Cita"
        verbose_name_plural = "Estados de Citas"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['reflexo', 'name'], name='uniq_appt_status_per_reflexo_name')
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Evita duplicados por (reflexo, name) con mensaje amigable en Admin.
        La restricción de BD ya existe; esto mejora el feedback del formulario.
        """
        if self.reflexo_id is None or not self.name:
            return
        qs = AppointmentStatus.objects.filter(reflexo_id=self.reflexo_id, name__iexact=self.name)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            from django.core.exceptions import ValidationError
            raise ValidationError({'name': ['Ya existe un estado con este nombre en esta empresa (tenant).']})
    
    @property
    def appointments_count(self):
        """Retorna el número de citas con este estado"""
        return self.appointment_set.count()
