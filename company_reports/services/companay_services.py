import os
import re
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image
from company_reports.models.company import CompanyData


class LogoValidationService:
    """Responsable exclusivamente de validar archivos de logos."""
    
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    
    @classmethod
    def validate_file_size(cls, file):
        """Valida que el archivo no exceda el tamaño máximo."""
        if file.size > cls.MAX_FILE_SIZE:
            raise ValueError(f"El logo excede el tamaño máximo permitido de {cls.MAX_FILE_SIZE} bytes.")
    
    @classmethod
    def validate_file_extension(cls, filename):
        """Valida que la extensión del archivo sea permitida."""
        ext = filename.split('.')[-1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Formato no permitido. Solo se aceptan: {', '.join(cls.ALLOWED_EXTENSIONS)}")
    
    @classmethod
    def validate_image_integrity(cls, file):
        """Valida que el archivo sea una imagen válida y no esté corrupta."""
        try:
            file.seek(0)
            with Image.open(file) as img:
                img.verify()
            file.seek(0)
        except Exception:
            raise ValueError("El archivo no es una imagen válida o está corrupta")
    
    @classmethod
    def validate(cls, file):
        """Valida completamente un archivo de logo."""
        cls.validate_file_size(file)
        cls.validate_file_extension(file.name)
        cls.validate_image_integrity(file)
        return file


class LogoFileManager:
    """Responsable exclusivamente del manejo de archivos de logos."""
    
    LOGO_FOLDER = 'company'
    
    @staticmethod
    def sanitize_file_name(filename):
        """Limpia el nombre del archivo (solo letras, números y guiones bajos)."""
        filename = filename.lower()
        filename = re.sub(r'[^a-z0-9]+', '_', filename)
        filename = filename.strip('_')
        return filename or 'company'
    
    @classmethod
    def generate_logo_file_name(cls, company_name, original_filename):
        """Genera un nombre seguro para el logo."""
        ext = os.path.splitext(original_filename)[1].lower().lstrip('.')
        if ext not in LogoValidationService.ALLOWED_EXTENSIONS:
            raise ValueError(f"Formato no permitido. Solo {', '.join(LogoValidationService.ALLOWED_EXTENSIONS)}")
        clean_name = cls.sanitize_file_name(company_name)
        return os.path.join(cls.LOGO_FOLDER, f"{clean_name}_logo.{ext}")
    
    @classmethod
    def save_logo_file(cls, company_name, file):
        """Guarda el archivo del logo y retorna la ruta guardada."""
        file_path = cls.generate_logo_file_name(company_name, file.name)
        return default_storage.save(file_path, file)
    
    @classmethod
    def delete_logo_file(cls, file_path):
        """Elimina un archivo de logo específico."""
        if file_path and default_storage.exists(file_path):
            default_storage.delete(file_path)
    
    @classmethod
    def clear_all_logos(cls):
        """Elimina todos los logos de la carpeta company/."""
        folder_path = os.path.join(settings.MEDIA_ROOT, cls.LOGO_FOLDER)
        if os.path.exists(folder_path):
            _, files = default_storage.listdir(cls.LOGO_FOLDER)
            for f in files:
                default_storage.delete(os.path.join(cls.LOGO_FOLDER, f))


class CompanyBusinessService:
    """Responsable exclusivamente de la lógica de negocio de empresas."""
    
    @staticmethod
    def get_company(company_id, tenant_id=None):
        """Obtiene una empresa por ID, restringida por tenant si se provee tenant_id."""
        try:
            qs = CompanyData.objects.all()
            if tenant_id is not None:
                qs = qs.filter(reflexo_id=tenant_id)
            return qs.get(pk=company_id)
        except CompanyData.DoesNotExist:
            return None
    
    @staticmethod
    def validate_company_name(company_name):
        """Valida que el nombre de la empresa no esté vacío."""
        if not company_name or not company_name.strip():
            raise ValueError("El nombre de la empresa es requerido")
        return company_name.strip()
    
    @staticmethod
    def create_company(company_name, tenant_id=None):
        """Crea una nueva empresa asignada al tenant si se provee tenant_id."""
        company = CompanyData()
        company.company_name = company_name
        if tenant_id is not None:
            company.reflexo_id = tenant_id
        company.save()
        return company
    
    @staticmethod
    def update_company(company, company_name):
        """Actualiza el nombre de una empresa existente."""
        company.company_name = company_name
        company.save()
        return company


class CompanyService:
    """
    Servicio principal que coordina las operaciones de empresa.
    """
    
    @staticmethod
    def show(company_id, tenant_id=None):
        """Retorna los datos de la empresa, validando tenant cuando aplique."""
        return CompanyBusinessService.get_company(company_id, tenant_id)
    
    @staticmethod
    def store(data, tenant_id=None):
        """Crea o actualiza datos de la empresa, restringiendo por tenant y asignándolo en creación."""
        company_id = data.get('id')
        
        try:
            # Obtener o crear empresa con validación de tenant
            if company_id:
                company = CompanyBusinessService.get_company(company_id, tenant_id)
                if not company:
                    raise ValueError("Empresa no encontrada")
            else:
                company = CompanyData()
                if tenant_id is not None:
                    company.reflexo_id = tenant_id
            
            # Validar y procesar nombre
            company_name = CompanyBusinessService.validate_company_name(data.get('company_name', ''))
            company.company_name = company_name
            
            # Procesar logo si se envía
            if 'company_logo' in data:
                company.company_logo = data['company_logo']
            
            # Guardar empresa
            company.save()
            return company
            
        except Exception as e:
            raise ValueError(f"Error interno al guardar los datos: {str(e)}")
    
    @staticmethod
    def process_logo(company, logo_url):
        """Actualiza el logo de una empresa existente."""
        try:
            company.company_logo = logo_url
            company.save()
            return company
            
        except Exception as e:
            raise ValueError(f"Error al procesar el logo: {str(e)}")
    
    @staticmethod
    def clear_company_logo(company):
        """Elimina el logo de una empresa específica."""
        company.company_logo = None
        company.save()