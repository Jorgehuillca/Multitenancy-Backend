import re
from datetime import date
from rest_framework import serializers
from therapists.models import Therapist 
from ubi_geo.models import Region, Province, District
from ubi_geo.serializers import RegionSerializer, ProvinceSerializer, DistrictSerializer
from histories_configurations.models import DocumentType
from histories_configurations.serializers import DocumentTypeSerializer

class TherapistSerializer(serializers.ModelSerializer):
    # Serializadores anidados para mostrar datos completos
    region = RegionSerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    document_type = DocumentTypeSerializer(read_only=True)  # Para lectura
    
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
            'document_type',
            'document_number',
            'last_name_paternal',
            'last_name_maternal',
            'first_name',
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
            'profile_picture',
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