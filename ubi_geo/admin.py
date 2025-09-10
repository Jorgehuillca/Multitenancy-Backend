from django.contrib import admin
from ubi_geo.models.region import Region
from ubi_geo.models.province import Province
from ubi_geo.models.district import District
from architect.utils.tenant import filter_by_tenant, get_tenant, is_global_admin

class BaseTenantAdmin(admin.ModelAdmin):
    """Admin base para aislar por tenant (reflexo)."""
    tenant_field_name = 'reflexo'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_global_admin(request.user):
            return qs
        # Si el modelo no tiene campo tenant, no filtrar (global)
        model_fields = {f.name for f in self.model._meta.get_fields()}
        if self.tenant_field_name in model_fields:
            return filter_by_tenant(qs, request.user, field=self.tenant_field_name)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from django.db.models import ForeignKey
        if isinstance(db_field, ForeignKey):
            # Para admins globales, no filtrar ni limitar
            if is_global_admin(request.user):
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            # Limitar el propio campo tenant al tenant del usuario
            if db_field.name == self.tenant_field_name:
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    kwargs['queryset'] = db_field.remote_field.model.objects.filter(pk=tenant_id)
            else:
                # Para otros FKs con campo tenant, filtrar por tenant
                rel_model = db_field.remote_field.model
                if hasattr(rel_model, self.tenant_field_name):
                    kwargs['queryset'] = filter_by_tenant(rel_model.objects.all(), request.user, field=self.tenant_field_name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # Campo tenant solo de solo lectura para no-admins, si existe en el modelo
        try:
            model_fields = {f.name for f in self.model._meta.get_fields()}
        except Exception:
            model_fields = set()
        if (not is_global_admin(request.user)
            and self.tenant_field_name in model_fields
            and self.tenant_field_name not in ro):
            ro.append(self.tenant_field_name)
        # Añadir timestamps sólo si existen en el modelo
        for fname in ('created_at', 'updated_at', 'deleted_at'):
            if fname in model_fields and fname not in ro:
                ro.append(fname)
        return tuple(ro)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Prefijar el tenant del usuario sólo para no-admins
        if not is_global_admin(request.user):
            tenant_id = get_tenant(request.user)
            if 'reflexo' in form.base_fields and tenant_id is not None:
                form.base_fields['reflexo'].initial = tenant_id
        return form

    def save_model(self, request, obj, form, change):
        # Solo setear tenant si existe en el modelo
        model_fields = {f.name for f in obj._meta.get_fields()}
        if self.tenant_field_name in model_fields:
            if not is_global_admin(request.user):
                tenant_id = get_tenant(request.user)
                if tenant_id is not None:
                    setattr(obj, f"{self.tenant_field_name}_id", tenant_id)
        super().save_model(request, obj, form, change)

@admin.register(Region)
class RegionAdmin(BaseTenantAdmin):
    list_display = ("ubigeo_code", "name", "created_at")
    list_filter = ("created_at", "deleted_at")
    search_fields = ("name",)
    ordering = ("ubigeo_code", "name")

@admin.register(Province)
class ProvinceAdmin(BaseTenantAdmin):
    list_display = ("sequence", "ubigeo_code", "name", "region", "created_at")
    list_filter = ("region", "created_at", "deleted_at")
    search_fields = ("name", "region__name")
    # Ordenar por secuencia visual, luego por códigos
    ordering = ("sequence", "region__ubigeo_code", "ubigeo_code", "name")

@admin.register(District)
class DistrictAdmin(BaseTenantAdmin):
    list_display = ("sequence", "ubigeo_code", "name", "province", "created_at")
    list_filter = ("province__region", "province", "created_at", "deleted_at")
    search_fields = ("name", "province__name", "province__region__name")
    # Ordenar por secuencia visual, luego por códigos
    ordering = ("sequence", "province__region__ubigeo_code", "province__ubigeo_code", "ubigeo_code", "name")