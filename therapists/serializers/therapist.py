import re
from datetime import date
from rest_framework import serializers
from therapists.models import Therapist 
from ubi_geo.models import Region, Province, District
from ubi_geo.serializers import RegionSerializer, ProvinceSerializer, DistrictSerializer
from histories_configurations.models import DocumentType
from histories_configurations.serializers import DocumentTypeSerializer
from reflexo.models import Reflexo
from django.core.files.storage import default_storage
from django.conf import settings

class TherapistSerializer(serializers.ModelSerializer):
    # Serializadores anidados para mostrar datos completos
    region = RegionSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    document_type = DocumentTypeSerializer(read_only=True)  # Para lectura
    # Campo calculado para nombre completo
    full_name = serializers.SerializerMethodField(read_only=True)
    # Devolver URLs ya listas para usar
    profile_picture = serializers.SerializerMethodField(read_only=True)       # absoluta
    profile_picture_url = serializers.SerializerMethodField(read_only=True)   # relativa con MEDIA_URL
    # Tenant (empresa)
    reflexo_id = serializers.PrimaryKeyRelatedField(queryset=Reflexo.objects.all(), source='reflexo', required=False)
    reflexo_name = serializers.CharField(source='reflexo.name', read_only=True)
    
    # Campos para escritura (crear/actualizar)
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), 
        source='region', 
        write_only=True,
        required=False
    )
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), 
        source='province', 
        write_only=True,
        required=False
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), 
        source='district', 
        write_only=True,
        required=False
    )
    document_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(),
        source='document_type',
        write_only=True,
        error_messages={
            'does_not_exist': 'El tipo de documento seleccionado no existe.'
        }
    )

    # Alternativa: permitir enviar códigos ubigeo en lugar de IDs
    region_code = serializers.IntegerField(write_only=True, required=False, help_text="Código ubigeo de la región")
    province_code = serializers.IntegerField(write_only=True, required=False, help_text="Código ubigeo de la provincia")
    district_code = serializers.IntegerField(write_only=True, required=False, help_text="Código ubigeo del distrito")

    class Meta:
        model = Therapist
        fields = [
            'id',
            'reflexo_id', 'reflexo_name',
            'document_type',
            'document_number',
            'last_name_paternal',
            'last_name_maternal',
            'first_name', 'full_name',
            'birth_date',
            'gender',
            'personal_reference',
            'is_active',
            'phone',
            'email',
            'region',
            'province',
            'district',
            'address',
            'profile_picture', 'profile_picture_url',
            'created_at',
            'updated_at',
            'deleted_at',
            'region_id',
            'province_id',
            'district_id',
            'document_type_id',
            'region_code',
            'province_code',
            'district_code',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def _inject_fk_from_codes(self, attrs):
        """Si vienen region_code/province_code/district_code y faltan los *_id,
        resolver por ubigeo_code y colocarlos en attrs como objetos FK (region/province/district).
        """
        # Solo resolver si no vinieron los *_id explícitos
        region = attrs.get('region')
        province = attrs.get('province')
        district = attrs.get('district')
        init = getattr(self, 'initial_data', {}) or {}

        # Region
        if region is None and 'region_code' in init and init.get('region_code') not in (None, ''):
            try:
                code = int(init.get('region_code'))
                from ubi_geo.models import Region as Reg
                attrs['region'] = Reg.objects.get(ubigeo_code=code)
            except (ValueError, Reg.DoesNotExist):
                raise serializers.ValidationError({'region_code': 'Código de región inválido o no existe.'})

        # Province (requiere region resuelta para coherencia posterior)
        if province is None and 'province_code' in init and init.get('province_code') not in (None, ''):
            try:
                code = int(init.get('province_code'))
                from ubi_geo.models import Province as Prov
                attrs['province'] = Prov.objects.get(ubigeo_code=code)
            except (ValueError, Prov.DoesNotExist):
                raise serializers.ValidationError({'province_code': 'Código de provincia inválido o no existe.'})

        # District
        if district is None and 'district_code' in init and init.get('district_code') not in (None, ''):
            try:
                code = int(init.get('district_code'))
                from ubi_geo.models import District as Dist
                attrs['district'] = Dist.objects.get(ubigeo_code=code)
            except (ValueError, Dist.DoesNotExist):
                raise serializers.ValidationError({'district_code': 'Código de distrito inválido o no existe.'})
        return attrs

    def _compose_relative_media_url(self, name: str) -> str | None:
        """Compone una URL relativa basada en MEDIA_URL a partir del nombre almacenado en storage."""
        if not name:
            return None
        media_url = settings.MEDIA_URL if hasattr(settings, 'MEDIA_URL') else '/media/'
        if name.startswith(media_url) or name.startswith('http://') or name.startswith('https://'):
            # Si ya viene con prefijo MEDIA_URL, devolver tal cual; si es http(s), no tocar
            return name if name.startswith(media_url) else None
        clean = name.lstrip('/\\')
        return f"{media_url}{clean}"

    def get_full_name(self, obj):
        first = getattr(obj, 'first_name', '') or ''
        lp = getattr(obj, 'last_name_paternal', '') or ''
        lm = getattr(obj, 'last_name_maternal', '') or ''
        return " ".join([p for p in [first.strip(), lp.strip(), lm.strip()] if p])

    def get_profile_picture_url(self, obj):
        """Ruta relativa que empieza con MEDIA_URL, por ejemplo: /media/therapists/photos/img.png"""
        name = getattr(obj, 'profile_picture', None)
        return self._compose_relative_media_url(name) if isinstance(name, str) else None

    def get_profile_picture(self, obj):
        """URL absoluta lista para abrir en navegador, ej: http://localhost:8000/media/therapists/photos/img.png"""
        rel = self.get_profile_picture_url(obj)
        if not rel:
            return None
        request = getattr(self, 'context', {}).get('request')
        if request is not None:
            return request.build_absolute_uri(rel)
        # En caso no haya request en contexto, devolver relativa (fallback)
        return rel
        
    def validate(self, attrs):
        """
        Asegura coherencia jerárquica:
        province debe pertenecer a region
        district debe pertenecer a province
        """
        # Resolver alternativas por código antes de validar coherencia
        attrs = self._inject_fk_from_codes(attrs)
        region = attrs.get("region") or getattr(self.instance, "region", None)
        province = attrs.get("province") or getattr(self.instance, "province", None)
        district = attrs.get("district") or getattr(self.instance, "district", None)

        # Validar presencia: debe existir region/province/district por id o por code
        errors = {}
        init = getattr(self, 'initial_data', {}) or {}
        if region is None and not init.get('region_code'):
            errors['region_id'] = ["Este campo es requerido (o use region_code)."]
        if province is None and not init.get('province_code'):
            errors['province_id'] = ["Este campo es requerido (o use province_code)."]
        if district is None and not init.get('district_code'):
            errors['district_id'] = ["Este campo es requerido (o use district_code)."]
        if errors:
            raise serializers.ValidationError(errors)

        if province and region and province.region_id != region.id:
            raise serializers.ValidationError(
                "La provincia seleccionada no pertenece a la región."
            )
        if district and province and district.province_id != province.id:
            raise serializers.ValidationError(
                "El distrito seleccionado no pertenece a la provincia."
            )
        return attrs

    def validate_document_number(self, value):
        # Obtener el tipo de documento desde los datos iniciales o la instancia
        doc_type_id = self.initial_data.get("document_type_id")
        
        # Si no está en initial_data, intentar obtener de la instancia existente
        if not doc_type_id and self.instance:
            doc_type_id = self.instance.document_type_id
        
        if not doc_type_id:
            return value  # No podemos validar sin tipo de documento
        
        # Obtener el nombre del tipo de documento para las validaciones
        try:
            document_type = DocumentType.objects.get(id=doc_type_id)
            doc_type_name = document_type.name.upper()
        except DocumentType.DoesNotExist:
            # La validación de existencia se hará en document_type_id field
            return value

        # Validaciones según el tipo de documento
        if doc_type_name == "DNI":
            if not value.isdigit():
                raise serializers.ValidationError("El DNI debe contener solo números.")
            if not (8 <= len(value) <= 9):
                raise serializers.ValidationError(
                    "El DNI debe tener entre 8 y 9 dígitos."
                )

        elif doc_type_name == "CE" or "CARNE DE EXTRANJERIA" in doc_type_name:
            if not value.isdigit():
                raise serializers.ValidationError(
                    "El Carné de Extranjería debe contener solo números."
                )
            if len(value) > 12:
                raise serializers.ValidationError(
                    "El Carné de Extranjería debe tener máximo 12 dígitos."
                )

        elif doc_type_name == "PTP":
            if not value.isdigit():
                raise serializers.ValidationError("El PTP debe contener solo números.")
            if len(value) != 9:
                raise serializers.ValidationError(
                    "El PTP debe tener exactamente 9 dígitos."
                )

        elif doc_type_name == "CR" or "CARNE DE REFUGIADO" in doc_type_name:
            if not re.match(r"^[A-Za-z0-9]+$", value):
                raise serializers.ValidationError(
                    "El Carné de Refugiado debe contener solo letras y números."
                )

        elif doc_type_name == "PAS" or "PASAPORTE" in doc_type_name:
            if not re.match(r"^[A-Za-z0-9]+$", value):
                raise serializers.ValidationError(
                    "El Pasaporte debe contener solo letras y números."
                )

        return value

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_last_name_paternal(self, value):
        if not value.strip():
            raise serializers.ValidationError("El apellido paterno no puede estar vacío.")
        return value

    def validate_last_name_maternal(self, value):
        # Este campo puede ser null/blank, pero si tiene valor debe ser válido
        if value and not value.strip():
            raise serializers.ValidationError("El apellido materno no puede estar vacío.")
        return value

    def validate_personal_reference(self, value):
        if value and not re.match(r"^[A-Za-z0-9\s]+$", value):
            raise serializers.ValidationError(
                "La referencia personal solo puede contener letras y números."
            )
        return value

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("El teléfono debe contener solo dígitos.")
        if value and len(value) > 20:
            raise serializers.ValidationError(
                "El teléfono debe tener máximo 20 dígitos."
            )
        return value

    def validate_email(self, value):
        if value:
            pattern = r'^[A-Za-z0-9._%+-]+@gmail\.com$'
            if not re.match(pattern, value):
                raise serializers.ValidationError("El correo debe ser válido y terminar en @gmail.com (ejemplo: usuario@gmail.com).")
        return value

    def validate_birth_date(self, value):
        if value:
            today = date.today()

            # No permitir fechas futuras
            if value.date() > today:
                raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")

            # Calcular edad
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 18:
                raise serializers.ValidationError("El terapeuta debe tener al menos 18 años.")

        return value

    def validate_profile_picture(self, value):
        if not value:
            return value
        # Validar que sea una cadena válida (URL o path)
        if not isinstance(value, str):
            raise serializers.ValidationError(
                "La imagen debe ser una URL válida."
            )
        return value

    # Asegurar que los campos auxiliares *_code no lleguen al create/update del modelo
    def create(self, validated_data):
        validated_data.pop('region_code', None)
        validated_data.pop('province_code', None)
        validated_data.pop('district_code', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('region_code', None)
        validated_data.pop('province_code', None)
        validated_data.pop('district_code', None)
        return super().update(instance, validated_data)


class TherapistPhotoSerializer(serializers.ModelSerializer):
    """Serializer dedicado para subir/asignar la foto del terapeuta.
    Acepta:
    - photo_file (multipart/form-data)
    - photo_url (JSON con ruta relativa o con prefijo MEDIA_URL)
    Guarda la ruta relativa en Therapist.profile_picture (CharField)
    """

    photo_url = serializers.CharField(required=False, allow_blank=True)
    photo_file = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = Therapist
        fields = ['photo_url', 'photo_file']

    def validate(self, attrs):
        if not attrs.get('photo_file') and not attrs.get('photo_url'):
            raise serializers.ValidationError("Debes enviar 'photo_file' (multipart) o 'photo_url' (JSON)")
        return attrs

    def update(self, instance, validated_data):
        file = validated_data.pop('photo_file', None)
        if file is not None:
            folder = 'therapists/photos/'
            name = default_storage.save(folder + file.name, file)
            instance.profile_picture = name
        else:
            raw_value = str(validated_data.get('photo_url', ''))
            media_url = settings.MEDIA_URL if hasattr(settings, 'MEDIA_URL') else '/media/'
            if raw_value.startswith(media_url):
                raw_value = raw_value[len(media_url):]
            instance.profile_picture = raw_value.lstrip('/\\')
        instance.save(update_fields=['profile_picture'])
        return instance