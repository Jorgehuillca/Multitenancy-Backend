from django.db import models
from django.utils import timezone

class ActivePatientManager(models.Manager):
    """Manager por defecto que excluye registros soft-deleted."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Patient(models.Model):
    """
    Modelo para gestionar los pacientes.
    Basado en la estructura de la tabla patients de la BD.
    """

    #Multitenant
    reflexo = models.ForeignKey(
        'reflexo.Reflexo', 
        on_delete=models.CASCADE, 
        related_name='+',
        null=True,      # permite que sea vacío temporalmente
        blank=True      # permite que el formulario del admin lo deje vacío
    )
    
    # Información personal
    document_number = models.CharField(max_length=20, unique=True, verbose_name="Número de documento")
    paternal_lastname = models.CharField(
    max_length=150, null=True, blank=True,
    db_column="last_name_paternal", verbose_name="Apellido paterno"
    )
    maternal_lastname = models.CharField(
    max_length=150, null=True, blank=True,
    db_column="last_name_maternal", verbose_name="Apellido materno"
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")
    personal_reference = models.CharField(max_length=255, blank=True, null=True, verbose_name="Referencia personal")
    birth_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de nacimiento")
    sex = models.CharField(max_length=50, blank=True, null=True,db_column="gender", verbose_name="Sexo")

    # Información de contacto
    phone1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono 1")
    phone2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono 2")
    email = models.CharField(max_length=254, verbose_name="Email")

    # Información adicional
    ocupation = models.CharField(max_length=100, verbose_name="Ocupación")
    health_condition = models.TextField(verbose_name="Condición de salud")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")

    # Relaciones con otras apps
    region = models.ForeignKey('ubi_geo.Region', on_delete=models.CASCADE, verbose_name="Región")
    province = models.ForeignKey('ubi_geo.Province', on_delete=models.CASCADE, verbose_name="Provincia")
    district = models.ForeignKey('ubi_geo.District', on_delete=models.CASCADE, verbose_name="Distrito")

    # Usando el modelo de DocumentType de histories_configurations
    document_type = models.ForeignKey(
        'histories_configurations.DocumentType',
        on_delete=models.CASCADE,
        verbose_name="Tipo de documento"
    )

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de eliminación")

    # Managers
    objects = ActivePatientManager()     # por defecto oculta eliminados
    all_objects = models.Manager()       # acceso a todos (incluidos eliminados)

    class Meta:
        db_table = 'patients'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete del paciente."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """Restaura un paciente eliminado."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    def get_full_name(self):
        """Obtiene el nombre completo del paciente."""
        return f"{self.name} {self.paternal_lastname} {self.maternal_lastname}"

    def __str__(self):
        return self.get_full_name()
