from django.contrib import admin
from django import forms
from .models.payment_type import PaymentType
from .models.document_type import DocumentType
from .models.history import History
from .models.predetermined_price import PredeterminedPrice
from .models import PaymentStatus
from architect.utils.tenant import filter_by_tenant, get_tenant, is_global_admin

class BaseTenantAdmin(admin.ModelAdmin):
    """Admin base para aislar por tenant (reflexo)."""
    tenant_field_name = 'reflexo'
    # No readonly fields by default; we'll add dynamically if they exist on the model

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_global_admin(request.user):
            return qs
        # Si el modelo no tiene campo tenant, no filtrar
        model_fields = {f.name for f in self.model._meta.get_fields()}
        if self.tenant_field_name in model_fields:
            return filter_by_tenant(qs, request.user, field=self.tenant_field_name)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrar FKs por tenant para evitar ver entidades de otros tenants
        from django.db.models import ForeignKey
        field_name = db_field.name
        if isinstance(db_field, ForeignKey):
            if is_global_admin(request.user):
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            # Filtrar el propio campo tenant si es FK
            if field_name == self.tenant_field_name:
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    kwargs['queryset'] = db_field.remote_field.model.objects.filter(pk=tenant_id)
            else:
                # Para otros FKs, intentar filtrar por el mismo campo tenant si existe
                rel_model = db_field.remote_field.model
                if hasattr(rel_model, self.tenant_field_name):
                    kwargs['queryset'] = filter_by_tenant(rel_model.objects.all(), request.user, field=self.tenant_field_name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # El campo tenant solo es de solo lectura para usuarios no admin, si existe
        try:
            model_fields = {f.name for f in self.model._meta.get_fields()}
        except Exception:
            model_fields = set()
        if (not is_global_admin(request.user)
            and self.tenant_field_name in model_fields
            and self.tenant_field_name not in ro):
            ro.append(self.tenant_field_name)
        # Agregar timestamps solamente si existen en el modelo
        for fname in ('created_at', 'updated_at', 'deleted_at'):
            if fname in model_fields and fname not in ro:
                ro.append(fname)
        return tuple(ro)

    def save_model(self, request, obj, form, change):
        # Asignar tenant automáticamente solo para no-admins o si no viene seteado
        tenant_id = get_tenant(request.user)
        model_fields = {f.name for f in obj._meta.get_fields()}
        if self.tenant_field_name in model_fields:
            if not is_global_admin(request.user):
                if tenant_id is not None:
                    setattr(obj, f"{self.tenant_field_name}_id", tenant_id)
            else:
                # Si es admin y no escogió tenant, usar el suyo si existe
                if getattr(obj, f"{self.tenant_field_name}_id", None) is None and tenant_id is not None:
                    setattr(obj, f"{self.tenant_field_name}_id", tenant_id)
        super().save_model(request, obj, form, change)

#Registrar el modelo en el admin
@admin.register(PaymentType)
class PaymentTypeAdmin(BaseTenantAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(DocumentType)
class DocumentTypeAdmin(BaseTenantAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

class HistoryAdminForm(forms.ModelForm):
    class Meta:
        model = History
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        required_errors = {}
        # Campos obligatorios solicitados
        if cleaned.get('height') in (None, ''):
            required_errors['height'] = 'Requerido'
        if cleaned.get('weight') in (None, ''):
            required_errors['weight'] = 'Requerido'
        if cleaned.get('last_weight') in (None, ''):
            required_errors['last_weight'] = 'Requerido'
        if cleaned.get('diu_type') in (None, ''):
            required_errors['diu_type'] = 'Requerido'
        if required_errors:
            from django.core.exceptions import ValidationError
            raise ValidationError(required_errors)
        return cleaned

@admin.register(History)
class HistoryAdmin(BaseTenantAdmin):
    # Ajuste dinámico de columnas y búsqueda según rol
    list_display = ('local_id', 'patient', 'reflexo', 'testimony', 'height', 'weight', 'created_at')
    list_filter = ('testimony', 'created_at', 'deleted_at')
    search_fields = ('local_id', 'patient__name', 'patient__document_number')
    form = HistoryAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Prefijar el valor de reflexo solo para usuarios no admin
        if not is_global_admin(request.user):
            tenant_id = get_tenant(request.user)
            if 'reflexo' in form.base_fields and tenant_id is not None:
                form.base_fields['reflexo'].initial = tenant_id
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ocultar historiales cuyo paciente fue eliminado lógicamente
        qs = qs.filter(patient__deleted_at__isnull=True)
        if is_global_admin(request.user):
            return qs
        return filter_by_tenant(qs, request.user, field='reflexo')

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # No permitir editar el tenant para usuarios no-admin
        if not is_global_admin(request.user) and 'reflexo' not in ro:
            ro.append('reflexo')
        # No permitir editar el ID local (siempre autogenerado)
        if 'local_id' not in ro:
            ro.append('local_id')
        return tuple(ro)

    def get_list_display(self, request):
        base = list(self.list_display)
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Siempre ocultar pacientes soft-deleted en el selector
        if db_field.name == 'patient':
            from patients_diagnoses.models import Patient
            base_qs = Patient.objects.filter(deleted_at__isnull=True)
            if not is_global_admin(request.user):
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    base_qs = base_qs.filter(reflexo_id=tenant_id)
            kwargs['queryset'] = base_qs
        elif db_field.name == 'reflexo':
            from reflexo.models import Reflexo
            if not is_global_admin(request.user):
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    kwargs['queryset'] = Reflexo.objects.filter(id=tenant_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Alinear reflexo con el paciente si es posible
        patient_tid = getattr(getattr(obj, 'patient', None), 'reflexo_id', None)
        if patient_tid and obj.reflexo_id and obj.reflexo_id != patient_tid:
            # Forzar coincidencia para evitar inconsistencias
            obj.reflexo_id = patient_tid
        if not is_global_admin(request.user):
            # Asegurar tenant del usuario
            obj.reflexo_id = get_tenant(request.user) or patient_tid or obj.reflexo_id

        # Asignar local_id secuencial si está vacío
        if getattr(obj, 'local_id', None) in (None, 0):
            from django.db import transaction
            from django.db.models import Max
            with transaction.atomic():
                max_local = (
                    History.objects.select_for_update()
                    .filter(reflexo_id=obj.reflexo_id)
                    .aggregate(m=Max('local_id'))['m']
                )
                obj.local_id = (max_local or 0) + 1

        super().save_model(request, obj, form, change)

@admin.register(PredeterminedPrice)
class PredeterminedPriceAdmin(BaseTenantAdmin):
    list_display = ('local_id', 'name', 'price', 'created_at')
    search_fields = ('local_id', 'name')
    ordering = ('reflexo_id', 'local_id', 'name')

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if 'local_id' not in ro:
            ro.append('local_id')
        return tuple(ro)

    def save_model(self, request, obj, form, change):
        # Asegurar tenant para no-admins o cuando no se especifica
        tenant_id = get_tenant(request.user)
        if not is_global_admin(request.user):
            if tenant_id is not None:
                obj.reflexo_id = tenant_id
        elif getattr(obj, 'reflexo_id', None) is None and tenant_id is not None:
            obj.reflexo_id = tenant_id

        # Asignar local_id secuencial por tenant si está vacío
        if getattr(obj, 'local_id', None) in (None, 0):
            from django.db import transaction
            from django.db.models import Max
            from .models.predetermined_price import PredeterminedPrice as PP
            with transaction.atomic():
                max_local = (
                    PP.objects.select_for_update()
                    .filter(reflexo_id=obj.reflexo_id)
                    .aggregate(m=Max('local_id'))['m']
                )
                obj.local_id = (max_local or 0) + 1

        super().save_model(request, obj, form, change)

@admin.register(PaymentStatus)
class PaymentStatusAdmin(BaseTenantAdmin):
    search_fields = ['name', 'description']  # necesario para el autocompletado
    list_display = ['name', 'description']
