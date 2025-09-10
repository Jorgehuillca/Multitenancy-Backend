from rest_framework import serializers
from ..models.diagnosis import Diagnosis
import re
from reflexo.models import Reflexo

class DiagnosisSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Diagnosis."""
    
    # Tenant (reflexo)
    reflexo_id = serializers.PrimaryKeyRelatedField(queryset=Reflexo.objects.all(), source='reflexo', required=False)
    reflexo_name = serializers.CharField(source='reflexo.name', read_only=True)

    class Meta:
        model = Diagnosis
        fields = [
            'id', 'code', 'name', 'reflexo_id', 'reflexo_name',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

    def validate_code(self, value):
        """Validar que el código solo contenga letras y números."""
        if not re.match(r'^[A-Za-z0-9]+$', value):
            raise serializers.ValidationError("El código solo debe contener letras y números.")
        if len(value) > 255:
            raise serializers.ValidationError("El código no debe superar los 255 caracteres.")
        
        # Validar unicidad por tenant (reflexo, code)
        reflexo_id = None
        if self.instance is not None:
            reflexo_id = getattr(self.instance, 'reflexo_id', None)
        if reflexo_id is None:
            reflexo_id = self.initial_data.get('reflexo_id') if isinstance(self.initial_data, dict) else None
        qs = Diagnosis.all_objects.filter(code=value)
        if reflexo_id is None:
            qs = qs.filter(reflexo__isnull=True)
        else:
            qs = qs.filter(reflexo_id=reflexo_id)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un diagnóstico con este código en la misma empresa (tenant).")
        return value

    def validate_name(self, value):
        """Validar que el nombre no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio.")
        return value

class DiagnosisListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar diagnósticos."""
    
    class Meta:
        model = Diagnosis
        fields = ['id', 'code', 'name', 'created_at']   