from django.db import models
from ubi_geo.models import Region, Province, District
from histories_configurations.models import DocumentType

class Therapist(models.Model):
    """
    Modelo para gestionar los terapeutas.
    Basado en la estructura de la tabla therapists de la BD.
    """
    #Multitenant
    reflexo = models.ForeignKey(
        'reflexo.Reflexo', 
        on_delete=models.CASCADE, 
        related_name='+',
        null=True,      # permite que sea vacío temporalmente
        blank=True      # permite que el formulario del admin lo deje vacío
    )
    
    # Datos personales
    document_type = models.ForeignKey(
        DocumentType, 
        on_delete=models.CASCADE,
        verbose_name="Tipo de documento"
    )
    document_number = models.CharField(max_length=20, unique=True, verbose_name="Número de documento")
    last_name_paternal = models.CharField(max_length=150, verbose_name="Apellido paterno")
    last_name_maternal = models.CharField(max_length=150, verbose_name="Apellido materno")
    first_name = models.CharField(max_length=150, verbose_name="Nombre")
    birth_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sexo")
    personal_reference = models.CharField(max_length=255, blank=True, null=True, verbose_name="Referencia personal")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    # Información de contacto
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.CharField(max_length=254, verbose_name="Email")

    # Ubicación
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Región")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name="Provincia")
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name="Distrito")

    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    profile_picture = models.CharField(max_length=255, blank=True, null=True, verbose_name="Foto de perfil")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de eliminación")

    def soft_delete(self):
        """Marca el registro como eliminado lógicamente."""
        from django.utils import timezone
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"]) 

    def restore(self):
        """Restaura un registro eliminado lógicamente."""
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save(update_fields=["deleted_at"]) 

    def get_full_name(self):
        """Obtiene el nombre completo del terapeuta."""
        return f"{self.first_name} {self.last_name_paternal} {self.last_name_maternal or ''}"
    
    def __str__(self):
        return self.get_full_name()

    class Meta:
        db_table = 'therapists'
        verbose_name = "Terapeuta"
        verbose_name_plural = "Terapeutas"
        ordering = ['first_name', 'last_name_paternal']