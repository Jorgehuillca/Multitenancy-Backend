from django.contrib import admin
from therapists.models.therapist import Therapist
from architect.utils.tenant import is_global_admin, get_tenant, filter_by_tenant

@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name_paternal", "document_number", "region", "province", "district", "deleted_at")
    list_filter = ("region", "province", "district", "created_at", "deleted_at")
    search_fields = ("first_name", "last_name_paternal", "last_name_maternal", "document_number")
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ocultar SIEMPRE los eliminados lógicamente
        qs = qs.filter(deleted_at__isnull=True)
        if is_global_admin(request.user):
            return qs
        return filter_by_tenant(qs, request.user, field='reflexo')

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not is_global_admin(request.user):
            # No permitir editar el tenant directamente
            ro.append('reflexo')
        return tuple(ro)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limitar selección de tenant y entidades relacionadas por tenant
        if db_field.name == 'reflexo' and not is_global_admin(request.user):
            tenant_id = get_tenant(request.user)
            if tenant_id is not None:
                from reflexo.models import Reflexo
                kwargs["queryset"] = Reflexo.objects.filter(id=tenant_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Asignar tenant automáticamente si no es admin global
        if not is_global_admin(request.user):
            obj.reflexo_id = get_tenant(request.user)
        super().save_model(request, obj, form, change)
