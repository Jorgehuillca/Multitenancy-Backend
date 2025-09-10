from rest_framework import serializers
from ..models import AppointmentStatus
from architect.utils.tenant import get_tenant


class AppointmentStatusSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo AppointmentStatus.
    Basado en la estructura actualizada del modelo.
    """
    
    # Campo calculado
    appointments_count = serializers.ReadOnlyField()
    
    class Meta:
        model = AppointmentStatus
        fields = [
            'id',
            'name',
            'description',
            'appointments_count',
            'created_at',
            'updated_at',
            'deleted_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'appointments_count']
    
    def validate_name(self, value):
        """Validación personalizada para el nombre del estado"""
        # Verificar que el nombre no esté vacío
        if not value.strip():
            raise serializers.ValidationError(
                "El nombre del estado no puede estar vacío."
            )
        
        # Verificar que no exista otro estado con el mismo nombre
        instance = self.instance
        # Limitar por tenant del request
        tenant_id = get_tenant(self.context.get('request').user) if self.context.get('request') else None
        qs = AppointmentStatus.objects.all()
        if tenant_id is not None:
            qs = qs.filter(reflexo_id=tenant_id)
        if qs.filter(name=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError(
                "Ya existe un estado de cita con este nombre."
            )
        
        return value.strip()
    
    def validate(self, data):
        """Validación a nivel de objeto"""
        name = data.get('name', '')
        description = data.get('description', '')
        
        # Si no hay descripción, usar el nombre como descripción
        if not description and name:
            data['description'] = name
        
        return data
