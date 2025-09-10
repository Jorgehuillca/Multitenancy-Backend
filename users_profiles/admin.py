from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from architect.utils.tenant import is_global_admin, get_tenant, filter_by_tenant

from .models.user_verification_code import UserVerificationCode

User = get_user_model()

# Evita AlreadyRegistered si alguien ya lo registró
try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Admin para el CustomUser sin username/first_name/last_name.
    USERNAME_FIELD = 'email'
    """
    # === Listado ===
    list_display = (
        "user_name",          # <- antes 'username'
        "email",
        "name",               # <- antes 'first_name'
        "paternal_lastname",
        "maternal_lastname",
        "sex",
        "reflexo",            # <- mostrar tenant
        "is_active",
        "is_staff",
        "created_at",         # usa tus campos reales
        "updated_at",
    )
    list_display_links = ("user_name", "email")
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "sex",
        "reflexo",            # <- filtrar por tenant
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user_name",
        "email",
        "name",
        "paternal_lastname",
        "maternal_lastname",
        "document_number",
        "phone",
    )
    ordering = ("-updated_at", "-created_at")

    # === Formularios ===
    fieldsets = (
        ("Credenciales", {
            "fields": ("email", "password")  # <- quita 'username'
        }),
        ("Información personal", {
            "fields": (
                "user_name",          # <- tu alias de usuario
                "name",
                "paternal_lastname",
                "maternal_lastname",
                "sex",
                "photo_url",
                "phone",
                "document_type",
                "document_number",
                "country",
                "account_statement",
                "password_change",
                "email_verified_at",
            ),
        }),
        ("Multi-tenant", {
            "fields": ("reflexo",),
            "description": "Empresa/Tenant al que pertenece el usuario"
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Fechas", {
            "classes": ("collapse",),
            "fields": ("last_login", "created_at", "updated_at", "deleted_at"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            # BaseUserAdmin respeta esto; como USERNAME_FIELD es 'email',
            # basta con incluir 'email' aquí. Incluimos también 'user_name'
            # para capturarlo al crear el usuario.
            "fields": ("email", "user_name", "password1", "password2"),
        }),
    )

    readonly_fields = ("last_login", "created_at", "updated_at", "email_verified_at")

    # Opcional: mejora UX en permisos
    filter_horizontal = ("groups", "user_permissions")

    # === Multi-tenant methods ===
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_global_admin(request.user):
            return qs
        return filter_by_tenant(qs, request.user, field='reflexo')

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not is_global_admin(request.user):
            ro.append('reflexo')
        return tuple(ro)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'reflexo' and not is_global_admin(request.user):
            tenant_id = get_tenant(request.user)
            if tenant_id is not None:
                from reflexo.models import Reflexo
                kwargs['queryset'] = Reflexo.objects.filter(id=tenant_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not is_global_admin(request.user):
            obj.reflexo_id = get_tenant(request.user)
        super().save_model(request, obj, form, change)


# =======================
# UserVerificationCode
# =======================

def _get(obj, *names, default="—"):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default

@admin.display(description="Tipo verificación")
def col_verification_type(obj):
    return _get(obj, "verification_type", "type")

@admin.display(description="Email destino")
def col_target_email(obj):
    return _get(obj, "target_email", "email")

@admin.display(boolean=True, description="Usado")
def col_is_used(obj):
    return bool(_get(obj, "is_used", "used", default=False))

@admin.display(description="Intentos")
def col_attempts(obj):
    return _get(obj, "attempts", "attempt_count", default=0)

@admin.display(description="Máx. intentos")
def col_max_attempts(obj):
    return _get(obj, "max_attempts", default="—")

@admin.display(description="Creado")
def col_created_at(obj):
    return _get(obj, "created_at", default="—")

@admin.display(description="Expira")
def col_expires_at(obj):
    return _get(obj, "expires_at", default="—")


class UsedListFilter(admin.SimpleListFilter):
    title = "Estado (usado)"
    parameter_name = "used"

    def lookups(self, request, model_admin):
        return (("yes", "Usado"), ("no", "No usado"))

    def queryset(self, request, queryset):
        val = self.value()
        if val == "yes":
            return queryset.filter(Q(is_used=True) | Q(used=True))
        if val == "no":
            return queryset.filter(
                Q(is_used=False) | Q(used=False) | Q(is_used__isnull=True) | Q(used__isnull=True)
            )
        return queryset


class VerificationTypeListFilter(admin.SimpleListFilter):
    title = "Tipo de verificación"
    parameter_name = "vtype"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        values = set(qs.values_list("verification_type", flat=True)) | set(qs.values_list("type", flat=True))
        values = sorted([v for v in values if v])
        return tuple((v, v) for v in values)

    def queryset(self, request, queryset):
        v = self.value()
        if not v:
            return queryset
        return queryset.filter(Q(verification_type=v) | Q(type=v))


@admin.register(UserVerificationCode)
class UserVerificationCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code",
        "failed_attempts",
        "locked_until",
        "expires_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("expires_at", "created_at", "updated_at")
    search_fields = (
        "user__user_name",  # si tu User tiene user_name
        "user__email",
        "code",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Información Básica", {"fields": ("user", "code")}),
        ("Estado", {"fields": ("failed_attempts", "locked_until")}),
        ("Vigencia", {"fields": ("expires_at",)}),
        ("Auditoría", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        # Evitar hits a la BD cuando la tabla no existe; el EmptyQuerySet no consulta.
        try:
            qs = super().get_queryset(request)
            return qs.select_related("user")
        except Exception:
            from django.db.models.query import EmptyQuerySet
            return self.model.objects.none()

    # Redirige el listado al formulario de creación para evitar el error de tabla inexistente
    def changelist_view(self, request, extra_context=None):
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse('admin:users_profiles_userverificationcode_add'))


# Configuración del sitio admin
admin.site.site_header = "Administración de Usuarios"
admin.site.site_title = "Usuarios"
admin.site.index_title = "Panel de Administración"
