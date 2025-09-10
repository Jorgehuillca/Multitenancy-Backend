from django.db import models


class Permission(models.Model):
    """
    Modelo para gestionar los permisos.
    Basado en la estructura de la tabla permissions de la BD.
    """
    
    name = models.CharField(max_length=255, verbose_name="Nombre")
    detail = models.CharField(max_length=255, blank=True, null=True, verbose_name="Detalle")
    guard_name = models.CharField(max_length=255, verbose_name="Guard name")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        db_table = 'permissions'
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RoleEnum(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    MEMBER = 'Member', 'Member'


class Role(models.Model):
    """
    Modelo para gestionar los roles.
    Basado en la estructura de la tabla roles de la BD.
    """
    
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre del Rol")
    guard_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Guard name")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        db_table = 'roles'
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['name']
        # Custom Django permission to allow cross-tenant visibility in admin/UI
        permissions = [
            ("view_all_tenants", "Can view data across all tenants (disable tenant filtering)"),
        ]
    
    def __str__(self):
        return self.name or "Sin nombre"
    
    @classmethod
    def get_admin_role(cls):
        return cls.objects.get_or_create(name=RoleEnum.ADMIN)[0]
    
    @classmethod
    def get_member_role(cls):
        return cls.objects.get_or_create(name=RoleEnum.MEMBER)[0] 