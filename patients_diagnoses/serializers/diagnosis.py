from rest_framework import serializers
from ..models.diagnosis import Diagnosis
import re
from reflexo.models import Reflexo

class DiagnosisSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Diagnosis.
    Los diagnósticos ahora son GLOBALES (no tenant). Se mantienen campos de reflexo solo en lectura
    por compatibilidad cuando existan valores legacy.
    """
    # Tenant (legacy/compatibilidad): solo lectura
    reflexo_id = serializers.IntegerField(read_only=True, required=False)
    reflexo_name = serializers.CharField(source='reflexo.name', read_only=True, required=False)

    class Meta:
        model = Diagnosis
        fields = [
            'id', 'code', 'name',
            'reflexo_id', 'reflexo_name',  # legacy (solo lectura)
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

    def validate_code(self, value):
        """Validar que el código solo contenga letras y números."""
        if not re.match(r'^[A-Za-z0-9]+$', value):
            raise serializers.ValidationError("El código solo debe contener letras y números.")
        if len(value) > 255:
            raise serializers.ValidationError("El código no debe superar los 255 caracteres.")
        # Unicidad GLOBAL por código (no-tenant)
        qs = Diagnosis.all_objects.filter(code=value)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un diagnóstico con este código.")
        return value

    def validate_name(self, value):
        """Validar que el nombre no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio.")
        return value

    # Forzar globalidad (reflexo=None)
    def create(self, validated_data):
        # eliminar cualquier rastro de 'reflexo' que pudiera llegar
        validated_data.pop('reflexo', None)
        obj = Diagnosis.objects.create(reflexo=None, **validated_data)
        return obj

    def update(self, instance, validated_data):
        # impedir cambios de tenant
        validated_data.pop('reflexo', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.reflexo_id = None
        instance.save()
        return instance

class DiagnosisListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar diagnósticos."""
    
    class Meta:
        model = Diagnosis
        fields = ['id', 'code', 'name', 'created_at']   