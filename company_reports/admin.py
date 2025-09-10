from django.contrib import admin
from company_reports.models.company import CompanyData
from django.http import HttpResponseRedirect
from django.urls import reverse
from architect.utils.tenant import is_global_admin, get_tenant

@admin.register(CompanyData)
class CompanyDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'company_logo', 'created_at', 'updated_at')
    search_fields = ('company_name',)
    ordering = ('company_name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('company_name', 'company_logo')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Ocultar completamente este admin para usuarios no globales (no aparece en el índice)
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        if not is_global_admin(request.user):
            return {}
        return perms

    # Si el usuario no es global y entra por un link (recent actions), redirigir a su tenant de Reflexo
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not is_global_admin(request.user):
            # En lugar de 403, lo enviamos al listado de Reflexo (acotado por tenant)
            return HttpResponseRedirect(reverse('admin:reflexo_reflexo_changelist'))
        return super().change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        if not is_global_admin(request.user):
            return HttpResponseRedirect(reverse('admin:reflexo_reflexo_changelist'))
        return super().changelist_view(request, extra_context)

    # Evitar 403 antes de llegar a change_view/changelist_view por permisos
    def has_view_permission(self, request, obj=None):
        # Permitir el acceso a la vista; el redireccionamiento protegerá a usuarios no globales
        return True

    def has_change_permission(self, request, obj=None):
        # Permitir que resuelva la view; el redireccionamiento decide
        return True

