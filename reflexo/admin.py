from django.contrib import admin
from .models import Reflexo
from architect.utils.tenant import is_global_admin, get_tenant

@admin.register(Reflexo)
class ReflexoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_global_admin(request.user):
            return qs
        tid = get_tenant(request.user)
        if tid is None:
            return qs.none()
        return qs.filter(id=tid)

    def has_add_permission(self, request):
        # Solo admin global puede crear nuevos tenants
        return is_global_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        # Solo admin global puede borrar tenants
        return is_global_admin(request.user)