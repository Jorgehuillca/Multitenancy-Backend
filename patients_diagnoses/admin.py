from django.contrib import admin
from .models.patient import Patient
from .models.diagnosis import Diagnosis
from .models.medical_record import MedicalRecord
from architect.utils.tenant import is_global_admin, get_tenant, filter_by_tenant


class BaseTenantAdmin(admin.ModelAdmin):
    """Admin base para aislar por tenant (reflexo)."""
    tenant_field_name = 'reflexo'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_global_admin(request.user):
            return qs
        return filter_by_tenant(qs, request.user, field=self.tenant_field_name)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from django.db.models import ForeignKey
        if isinstance(db_field, ForeignKey):
            if is_global_admin(request.user):
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            # Limitar el selector del propio tenant siempre al tenant del usuario
            if db_field.name == self.tenant_field_name:
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    kwargs['queryset'] = db_field.remote_field.model.objects.filter(pk=tenant_id)
            else:
                # Para otros FKs, si el modelo relacionado tiene campo tenant, filtrarlo
                rel_model = db_field.remote_field.model
                if hasattr(rel_model, self.tenant_field_name):
                    kwargs['queryset'] = filter_by_tenant(rel_model.objects.all(), request.user, field=self.tenant_field_name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # El campo tenant solo de solo lectura para no-admins
        if not is_global_admin(request.user) and self.tenant_field_name not in ro:
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
        # Forzar tenant solo para no-admins; admin puede elegir
        tenant_id = get_tenant(request.user)
        if not is_global_admin(request.user):
            if tenant_id is not None:
                setattr(obj, f"{self.tenant_field_name}_id", tenant_id)
        else:
            if getattr(obj, f"{self.tenant_field_name}_id", None) is None and tenant_id is not None:
                setattr(obj, f"{self.tenant_field_name}_id", tenant_id)
        super().save_model(request, obj, form, change)

class CurrentTenantReflexoFilter(admin.SimpleListFilter):
    title = 'reflexo'
    parameter_name = 'reflexo'

    def lookups(self, request, model_admin):
        # Solo mostrar el tenant del usuario actual
        if is_global_admin(request.user):
            from reflexo.models import Reflexo
            return [(r.id, r.name) for r in Reflexo.objects.all().order_by('name')]
        tid = get_tenant(request.user)
        if tid is None:
            return []
        from reflexo.models import Reflexo
        name = Reflexo.objects.filter(id=tid).values_list('name', flat=True).first() or str(tid)
        return [(tid, name)]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(reflexo_id=value)
        # Si no hay valor y el usuario no es global, ya viene filtrado por get_queryset
        return queryset

@admin.register(Patient)
class PatientAdmin(BaseTenantAdmin):
    # Valores por defecto (se ajustan dinámicamente en get_list_display/get_search_fields)
    list_display = (
        'local_id', 'document_number', 'name', 'paternal_lastname', 'maternal_lastname',
        'phone1', 'email', 'reflexo'
    )
    search_fields = (
        'local_id', 'document_number', 'name', 'paternal_lastname', 'maternal_lastname', 'personal_reference'
    )
    list_filter = (
        'sex', 'region', 'province', 'district', 'document_type', 'created_at', 'deleted_at'
    )
    # readonly_fields dinámicos en BaseTenantAdmin

    def get_list_filter(self, request):
        base = list(super().get_list_filter(request))
        # Para usuarios de empresa, reemplazar el filtro de reflexo por uno acotado al tenant
        if is_global_admin(request.user):
            return tuple(['reflexo'] + base)
        return tuple([CurrentTenantReflexoFilter] + base)

    def get_list_display(self, request):
        base = list(self.list_display)
        # Para admins globales, incluir el ID global por conveniencia
        if is_global_admin(request.user):
            if 'id' not in base:
                base.insert(1, 'id')  # después de local_id
        else:
            # Asegurar que el ID global no aparezca para usuarios de empresa
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ocultar por defecto los eliminados (soft delete)
        return qs.filter(deleted_at__isnull=True)

    # readonly_fields manejados en BaseTenantAdmin

    # FKs filtrados por BaseTenantAdmin

    # Guardado con tenant por BaseTenantAdmin

    def changelist_view(self, request, extra_context=None):
        # Si el usuario de empresa no tiene tenant asignado, mostrar advertencia clara
        if not is_global_admin(request.user) and get_tenant(request.user) is None:
            from django.contrib import messages
            messages.warning(
                request,
                "Tu usuario no tiene una empresa asignada (reflexo). No se puede mostrar ningún paciente. Pide al admin que te asigne una empresa."
            )
        return super().changelist_view(request, extra_context)

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('row_number_display', 'code', 'name', 'created_at')
    search_fields = ('code', 'name')
    ordering = ('code',)
    # Diagnósticos son GLOBALES: no aplicar filtrado por tenant ni forzar reflexo

    def get_queryset(self, request):
        from django.db.models.expressions import Window
        from django.db.models.functions import RowNumber
        from django.db.models import F
        qs = super().get_queryset(request)
        # Ocultar por defecto los diagnósticos soft-deleted en el admin
        qs = qs.filter(deleted_at__isnull=True)
        # Numeración global y estable por código
        return qs.annotate(row_number=Window(expression=RowNumber(), order_by=F('code').asc()))

    def row_number_display(self, obj):
        return getattr(obj, 'row_number', None)
    row_number_display.short_description = 'N°'
    row_number_display.admin_order_field = 'row_number'

    def save_model(self, request, obj, form, change):
        # No forzar tenant (reflexo). Los diagnósticos son globales.
        return super().save_model(request, obj, form, change)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(BaseTenantAdmin):
    list_display = ('patient', 'diagnose', 'diagnosis_date', 'status', 'created_at')
    list_filter = ('status', 'diagnosis_date', 'created_at', 'deleted_at')
    search_fields = ('patient__name', 'patient__document_number', 'diagnose__name', 'diagnose__code')
    ordering = ('-diagnosis_date', '-created_at')
    # Autocomplete para datasets grandes (sólo paciente). Para diagnóstico usamos raw_id para evitar dropdown enorme.
    autocomplete_fields = ('patient',)
    raw_id_fields = ('diagnose',)
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('patient',)
        }),
        ('Información del Diagnóstico', {
            'fields': ('diagnose', 'diagnosis_date', 'status')
        }),
        ('Detalles Médicos', {
            'fields': ('symptoms', 'treatment', 'notes')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('patient', 'diagnose')
        # Ocultar por defecto los registros soft-deleted
        qs = qs.filter(deleted_at__isnull=True)
        if is_global_admin(request.user):
            return qs
        return filter_by_tenant(qs, request.user, field='reflexo')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limitar SIEMPRE a registros no eliminados
        if db_field.name == 'patient':
            base_qs = Patient.objects.filter(deleted_at__isnull=True)
            if not is_global_admin(request.user):
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    base_qs = base_qs.filter(reflexo_id=tenant_id)
            kwargs['queryset'] = base_qs
        elif db_field.name == 'diagnose':
            # Diagnósticos globales: NO filtrar por tenant.
            kwargs['queryset'] = Diagnosis.objects.filter(deleted_at__isnull=True)
            # Importante: delegar a super() para que Django aplique raw_id_fields
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
