from django.contrib import admin
from django import forms
from .models.appointment import Appointment
from .models.appointment_status import AppointmentStatus
from .models.ticket import Ticket
from architect.utils.tenant import is_global_admin, get_tenant, filter_by_tenant


class BaseTenantAdmin(admin.ModelAdmin):
    """Admin base que aísla por tenant (reflexo)."""
    tenant_field_name = 'reflexo'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return filter_by_tenant(qs, request.user, field=self.tenant_field_name)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from django.db.models import ForeignKey
        if isinstance(db_field, ForeignKey):
            if db_field.name == self.tenant_field_name:
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    kwargs['queryset'] = db_field.remote_field.model.objects.filter(pk=tenant_id)
            else:
                rel_model = db_field.remote_field.model
                if hasattr(rel_model, self.tenant_field_name):
                    kwargs['queryset'] = filter_by_tenant(rel_model.objects.all(), request.user, field=self.tenant_field_name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # El campo tenant siempre de solo lectura
        if self.tenant_field_name not in ro:
            ro.append(self.tenant_field_name)
        # Agregar timestamps si existen
        try:
            model_fields = {f.name for f in self.model._meta.get_fields()}
        except Exception:
            model_fields = set()
        for fname in ('created_at', 'updated_at', 'deleted_at'):
            if fname in model_fields and fname not in ro:
                ro.append(fname)
        return tuple(ro)

    def save_model(self, request, obj, form, change):
        tenant_id = get_tenant(request.user)
        if tenant_id is not None:
            setattr(obj, f"{self.tenant_field_name}_id", tenant_id)
        super().save_model(request, obj, form, change)


@admin.register(AppointmentStatus)
class AppointmentStatusAdmin(BaseTenantAdmin):
    """
    Configuración del admin para AppointmentStatus.
    """
    list_display = ['name', 'description', 'appointments_count', 'created_at']
    list_filter = ['created_at', 'updated_at', 'deleted_at']
    search_fields = ['name', 'description']
    # readonly_fields dinámicos + 'appointments_count'
    readonly_fields = ['appointments_count']
    ordering = ['name']

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description')
        }),
        ('Información del Sistema', {
            'fields': ('appointments_count', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# --- Inline opcional para crear/ver Tickets desde la Cita ---
class TicketInline(admin.StackedInline):
    model = Ticket
    extra = 0
    autocomplete_fields = ['appointment']  # no carga listas enormes
    readonly_fields = ['is_paid', 'is_pending', 'payment_date', 'created_at', 'updated_at', 'deleted_at']
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('ticket_number', 'amount', 'payment_method', 'description')
        }),
        ('Estado del Pago', {
            'fields': ('status',)
        }),
        ('Relaciones', {
            'fields': ('appointment',),
            'description': 'La cita se completa automáticamente al usar el inline.'
        }),
        ('Información del Sistema', {
            'fields': ('is_paid', 'is_pending', 'payment_date', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(BaseTenantAdmin):
    class AppointmentAdminForm(forms.ModelForm):
        class Meta:
            model = Appointment
            fields = '__all__'

        def clean(self):
            cleaned = super().clean()
            appt_dt = cleaned.get('appointment_date')
            hour = cleaned.get('hour')
            # Si viene appointment_date con hora incluida y sin hour, derivarlo
            if appt_dt is not None and hour is None and hasattr(appt_dt, 'time'):
                cleaned['hour'] = appt_dt.time()
            # Requerir siempre los 4 campos (crear y actualizar)
            required_errors = {}
            if cleaned.get('appointment_date') is None:
                required_errors['appointment_date'] = 'Requerido'
            if cleaned.get('hour') is None:
                required_errors['hour'] = 'Requerido'
            if cleaned.get('initial_date') is None:
                required_errors['initial_date'] = 'Requerido'
            if cleaned.get('final_date') is None:
                required_errors['final_date'] = 'Requerido'
            # Pago obligatorio
            if cleaned.get('payment') in (None, ''):
                required_errors['payment'] = 'Requerido'
            # Habitación/Consultorio obligatorio
            if cleaned.get('room') in (None, ''):
                required_errors['room'] = 'Requerido'
            # Estado de pago obligatorio
            if cleaned.get('payment_status') is None:
                required_errors['payment_status'] = 'Requerido'
            if required_errors:
                from django.core.exceptions import ValidationError
                raise ValidationError(required_errors)
            return cleaned

    form = AppointmentAdminForm
    list_display = [
        'local_id', 'appointment_date', 'hour', 'appointment_status',
        'room', 'is_completed', 'deleted_at'
    ]
    list_filter = [
        'appointment_date', 'appointment_status', 'room',
        'created_at', 'deleted_at'
    ]
    search_fields = ['local_id', 'ailments', 'diagnosis', 'observation', 'ticket_number']
    readonly_fields = ['is_completed', 'is_pending', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['reflexo_id', 'local_id', '-appointment_date', '-hour']

    # 👇 según prefieras
    raw_id_fields = ['patient', 'therapist', 'history']
    # o bien
    autocomplete_fields = ['payment_status']

    fieldsets = (
        ('Información de la Cita', {
            'fields': ('appointment_date', 'hour', 'room')
        }),
        ('Información Médica', {
            'fields': ('ailments', 'diagnosis', 'surgeries', 'reflexology_diagnostics', 'medications', 'observation')
        }),
        ('Fechas de Tratamiento', {
            'fields': ('initial_date', 'final_date')
        }),
        ('Información de Pago', {
            'fields': ('social_benefit', 'payment_detail', 'payment', 'ticket_number')
        }),
        ('Relaciones', {
            'fields': ('patient', 'therapist', 'history', 'payment_status', 'appointment_status'),
            'description': 'Selecciona paciente, terapeuta, historial y estado de pago.'
        }),
        ('Información del Sistema', {
            'fields': ('is_completed', 'is_pending', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = (super()
              .get_queryset(request)
              .select_related('patient', 'therapist', 'history', 'payment_status'))
        return filter_by_tenant(qs, request.user, field='reflexo')

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if 'local_id' not in ro:
            ro.append('local_id')
        return tuple(ro)

    def get_list_display(self, request):
        base = list(self.list_display)
        # Para admin global, mostrar también el id global
        if is_global_admin(request.user):
            if 'id' not in base:
                base.insert(1, 'id')
        else:
            base = [f for f in base if f != 'id']
        return tuple(base)

    def get_search_fields(self, request):
        base = list(self.search_fields)
        if is_global_admin(request.user):
            if 'id' not in base:
                base.insert(1, 'id')
        else:
            base = [f for f in base if f != 'id']
        return tuple(base)

    # readonly_fields manejados en BaseTenantAdmin

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        tenant_id = get_tenant(request.user)
        if tenant_id is not None and not is_global_admin(request.user):
            if db_field.name == 'patient':
                from patients_diagnoses.models import Patient
                kwargs['queryset'] = Patient.objects.filter(reflexo_id=tenant_id)
            elif db_field.name == 'therapist':
                from therapists.models import Therapist
                kwargs['queryset'] = Therapist.objects.filter(reflexo_id=tenant_id)
            elif db_field.name == 'history':
                from histories_configurations.models import History
                kwargs['queryset'] = History.objects.filter(reflexo_id=tenant_id)
            elif db_field.name == 'appointment_status':
                kwargs['queryset'] = AppointmentStatus.objects.filter(reflexo_id=tenant_id)
            elif db_field.name == 'reflexo':
                from reflexo.models import Reflexo
                kwargs['queryset'] = Reflexo.objects.filter(id=tenant_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Guardado asigna tenant en BaseTenantAdmin
    def save_model(self, request, obj, form, change):
        # Alinear tenant con patient/history si es posible
        patient_tid = getattr(getattr(obj, 'patient', None), 'reflexo_id', None)
        history_tid = getattr(getattr(obj, 'history', None), 'reflexo_id', None)
        target_tid = patient_tid or history_tid or obj.reflexo_id
        if target_tid:
            obj.reflexo_id = target_tid

        # Asignar local_id secuencial si está vacío
        if getattr(obj, 'local_id', None) in (None, 0):
            from django.db import transaction
            from django.db.models import Max
            with transaction.atomic():
                max_local = (
                    Appointment.objects.select_for_update()
                    .filter(reflexo_id=obj.reflexo_id)
                    .aggregate(m=Max('local_id'))['m']
                )
                obj.local_id = (max_local or 0) + 1

        super().save_model(request, obj, form, change)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Ticket.
    """
    list_display = [
        'ticket_number', 'amount', 'payment_method', 'status',
        'is_paid', 'payment_date', 'deleted_at'
    ]
    list_filter = [
        'payment_method', 'status', 'payment_date', 'created_at', 'deleted_at'
    ]
    search_fields = ['ticket_number', 'description']
    readonly_fields = ['is_paid', 'is_pending', 'payment_date', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-payment_date']

    # ✅ Para no cargar todas las citas en un <select>
    autocomplete_fields = ['appointment']  # (usa raw_id_fields = ['appointment'] si prefieres)

    fieldsets = (
        ('Información del Ticket', {
            'fields': ('ticket_number', 'amount', 'payment_method', 'description')
        }),
        ('Estado del Pago', {
            'fields': ('status',)
        }),
        ('Relaciones', {
            # ✅ Campo necesario para evitar el NOT NULL
            'fields': ('appointment',),
            'description': 'Selecciona la cita a la que pertenece este ticket'
        }),
        ('Información del Sistema', {
            'fields': ('is_paid', 'is_pending', 'payment_date', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_paid', 'mark_as_cancelled']

    def mark_as_paid(self, request, queryset):
        """Acción para marcar tickets como pagados"""
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} tickets marcados como pagados.')
    mark_as_paid.short_description = "Marcar como pagado"

    def mark_as_cancelled(self, request, queryset):
        """Acción para marcar tickets como cancelados"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} tickets marcados como cancelados.')
    mark_as_cancelled.short_description = "Marcar como cancelado"

    def get_queryset(self, request):
        """Optimiza las consultas con select_related y aplica tenant"""
        qs = super().get_queryset(request).select_related('appointment')
        if is_global_admin(request.user):
            return qs
        tenant_id = get_tenant(request.user)
        return qs.filter(appointment__reflexo_id=tenant_id)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'appointment' and not is_global_admin(request.user):
            tenant_id = get_tenant(request.user)
            if tenant_id is not None:
                kwargs['queryset'] = Appointment.objects.filter(reflexo_id=tenant_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        """
        Permite precargar la cita si vienes con ?appointment=<id> en la URL de alta:
        /admin/appointments_status/ticket/add/?appointment=123
        """
        initial = super().get_changeform_initial_data(request)
        aid = request.GET.get("appointment")
        if aid:
            initial["appointment"] = aid
        return initial
