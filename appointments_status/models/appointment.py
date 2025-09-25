from django.db import models
from django.db.models import Q
from django.utils import timezone
 


class Appointment(models.Model):
    """
    Modelo para gestionar las citas médicas.
    Basado en la estructura de la tabla appointments de la BD.
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

    # Relaciones con otros módulos
    history = models.ForeignKey('histories_configurations.History', on_delete=models.CASCADE, verbose_name="Historial")
    patient = models.ForeignKey('patients_diagnoses.Patient', on_delete=models.CASCADE, verbose_name="Paciente")
    therapist = models.ForeignKey('therapists.Therapist', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Terapeuta")
    
    # Campos principales de la cita
    appointment_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de la cita")
    hour = models.TimeField(blank=True, null=True, verbose_name="Hora de la cita")
    
    # Información médica
    ailments = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Padecimientos")
    diagnosis = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Diagnóstico")
    surgeries = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Cirugías")
    reflexology_diagnostics = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Diagnósticos de reflexología")
    medications = models.CharField(max_length=255, blank=True, null=True, verbose_name="Medicamentos")
    observation = models.CharField(max_length=255, blank=True, null=True, verbose_name="Observaciones")
    
    # Fechas de tratamiento
    initial_date = models.DateField(blank=True, null=True, verbose_name="Fecha inicial")
    final_date = models.DateField(blank=True, null=True, verbose_name="Fecha final")
    
    # Configuración de la cita
    appointment_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo de cita")
    room = models.IntegerField(blank=True, null=True, verbose_name="Habitación/Consultorio")
    
    # Información de pago
    social_benefit = models.BooleanField(default=True, verbose_name="Beneficio social")
    payment_detail = models.CharField(max_length=255, blank=True, null=True, verbose_name="Detalle de pago")
    payment = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Pago")
    ticket_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    
    # Relaciones
    payment_type = models.ForeignKey('histories_configurations.PaymentType', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de pago")
    payment_status = models.ForeignKey('histories_configurations.PaymentStatus', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Estado de pago")
    
    # Estado de la cita (relación a catálogo gestionado en AppointmentStatus)
    appointment_status = models.ForeignKey(
        'appointments_status.AppointmentStatus',
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name="Estado de la cita"
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de eliminación")
    
    class Meta:
        db_table = 'appointments'
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['reflexo_id', 'local_id', '-appointment_date', '-hour']
        indexes = [
            models.Index(fields=['appointment_date', 'hour']),
            models.Index(fields=['appointment_status']),
        ]
        constraints = [
            # Evita duplicar citas activas con el mismo par (patient, history)
            models.UniqueConstraint(
                fields=['patient', 'history'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_active_patient_history'
            ),
            # Unicidad del número de cita por empresa cuando local_id no es nulo
            models.UniqueConstraint(
                fields=['reflexo', 'local_id'],
                name='uniq_appointment_local_id_per_reflexo',
                condition=Q(local_id__isnull=False)
            )
        ]
    
    def __str__(self):
        num = self.local_id or self.id
        return f"Cita {num} - {self.appointment_date} {self.hour}"
    
    @property
    def is_completed(self):
        """Verifica si la cita está completada basándose en la fecha"""
        if self.appointment_date is None:
            return False
        return self.appointment_date.date() < timezone.now().date()

    @property
    def is_pending(self):
        """Verifica si la cita está pendiente"""
        if self.appointment_date is None:
            return False
        return self.appointment_date.date() >= timezone.now().date()

    def clean(self):
        """Validaciones de consistencia multi-tenant y relaciones.
        - patient, therapist y history deben pertenecer al mismo tenant (reflexo)
        - history.patient debe coincidir con patient
        - Asigna reflexo automáticamente si es determinable
        """
        errors = {}
        # Cargar FKs si existen
        patient = getattr(self, 'patient', None)
        therapist = getattr(self, 'therapist', None)
        history = getattr(self, 'history', None)

        # Validar que history pertenezca al mismo patient
        if history is not None and patient is not None and history.patient_id != patient.id:
            errors['history'] = ['El historial no pertenece al paciente proporcionado.']

        # Tenants
        p_tid = getattr(patient, 'reflexo_id', None) if patient else None
        t_tid = getattr(therapist, 'reflexo_id', None) if therapist else None
        h_tid = getattr(history, 'reflexo_id', None) if history else None

        # Si hay más de un tenant presente, deben coincidir
        tenants = [t for t in [p_tid, t_tid, h_tid, self.reflexo_id] if t is not None]
        if tenants and any(t != tenants[0] for t in tenants):
            # Usar '__all__' para que Django Admin muestre el error general
            errors['__all__'] = ['Paciente, terapeuta e historial deben pertenecer a la misma empresa (tenant).']

        # Si ya tenemos un tenant objetivo (por patient/history/reflexo) y el terapeuta no coincide, marcar error en el campo
        target_tid = p_tid or h_tid or self.reflexo_id
        if target_tid is not None and therapist is not None and t_tid is not None and t_tid != target_tid:
            errors['therapist'] = ['El terapeuta pertenece a una empresa (tenant) diferente a la del paciente/historial.']

        # Asignar reflexo automáticamente si no viene y se puede inferir
        if self.reflexo_id is None:
            inferred = p_tid or h_tid or t_tid
            if inferred is not None:
                self.reflexo_id = inferred

        # Evitar duplicados: una cita activa por par (patient, history)
        if patient is not None and history is not None:
            exists_dup = (
                Appointment.objects.filter(
                    patient_id=patient.id,
                    history_id=history.id,
                    deleted_at__isnull=True,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if exists_dup:
                errors['__all__'] = errors.get('__all__', []) + [
                    'Ya existe una cita activa para este paciente con este historial. Cree/seleccione otro historial para evitar duplicados.'
                ]

        if errors:
            from django.core.exceptions import ValidationError
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar (aplica para Admin y API)
        self.full_clean()
        super().save(*args, **kwargs)
