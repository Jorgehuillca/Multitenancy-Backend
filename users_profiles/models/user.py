# users_profiles/models/user.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import FileExtensionValidator



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Desactivar campos de AbstractUser que NO existen en tu tabla
    username   = None
    first_name = None
    last_name  = None

    # Login por email
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")

    # Mapear last_login (Django) -> last_session (tu tabla)
    last_login = models.DateTimeField(null=True, blank=True, db_column='last_session')

    # Campos propios...
    document_number = models.CharField(max_length=20, unique=True, verbose_name="Número de documento")
    user_name = models.CharField(max_length=50, unique=True, verbose_name="Nombre de usuario")
    photo_url = models.ImageField(upload_to="users/photos/", blank=True, null=True,
                                  verbose_name="Foto de perfil",
                                  validators=[FileExtensionValidator(allowed_extensions=["jpg","jpeg","png","gif"])])
    name = models.CharField(max_length=100, verbose_name="Nombres")
    paternal_lastname = models.CharField(max_length=100, verbose_name="Apellido paterno")
    maternal_lastname = models.CharField(max_length=100, verbose_name="Apellido materno")
    
    sex = models.CharField(max_length=1, choices=[('M','Masculino'),('F','Femenino'),('O','Otro')],
    blank=True, null=True, verbose_name="Sexo")
    
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")

    password_change   = models.BooleanField(default=False, verbose_name="Requiere cambio de contraseña")
    account_statement = models.CharField(max_length=1, default='A', verbose_name="Estado de cuenta")
    email_verified_at = models.DateTimeField(blank=True, null=True, verbose_name="Email verificado en")
    remember_token    = models.CharField(max_length=100, blank=True, null=True, verbose_name="Token de recordatorio")

    # Multitenant: empresa/tenant al que pertenece el usuario
    # Nota: se deja nullable para no romper usuarios existentes hasta migración/backfill
    reflexo = models.ForeignKey(
        'reflexo.Reflexo',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Empresa/Tenant'
    )

    document_type = models.ForeignKey('histories_configurations.DocumentType',
                                      on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de documento")
    country = models.ForeignKey('ubi_geo.Country',
                                on_delete=models.SET_NULL, null=True, blank=True, verbose_name="País")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Eliminado en")

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['user_name', 'document_number']

    class Meta:
        db_table = 'users'
        managed = True  # permitir que Django gestione/cree la tabla
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.name} {self.paternal_lastname} - {self.document_number}"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    def get_full_name(self):
        return f"{self.name} {self.paternal_lastname} {self.maternal_lastname}"

    def verify_email(self):
        self.email_verified_at = timezone.now()
        self.save(update_fields=['email_verified_at'])

    def clean(self):
        """Validación del modelo."""
        from django.core.exceptions import ValidationError
        
        # Validar que usuarios no superuser tengan tenant asignado
        if not self.is_superuser and not self.reflexo_id:
            raise ValidationError({
                'reflexo': 'Los usuarios deben tener un tenant asignado (excepto superusuarios)'
            })
        
        super().clean()

    @property
    def is_global_admin(self) -> bool:
        """Admin global (ve todo): superuser o rol Admin si existiera el atributo."""
        return bool(getattr(self, 'is_superuser', False) or getattr(self, 'rol', None) == 'Admin')
    
    def get_completion_percentage(self):
        """Calcula el porcentaje de completitud del perfil del usuario."""
        required_fields = ['name', 'email', 'phone']
        completed_fields = sum(1 for field in required_fields if getattr(self, field))
        completion_percentage = (completed_fields / len(required_fields)) * 100
        return round(completion_percentage, 2)