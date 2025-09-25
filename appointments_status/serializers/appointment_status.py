from rest_framework import serializers
from ..models import AppointmentStatus
from architect.utils.tenant import get_tenant
from architect.utils.tenant import is_global_admin
from reflexo.models import Reflexo


class AppointmentStatusSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo AppointmentStatus.
    Basado en la estructura actualizada del modelo.
    """
    
    # Tenant (solo admins pueden enviarlo)
    reflexo_id = serializers.PrimaryKeyRelatedField(
        queryset=Reflexo.objects.all(), source='reflexo', required=False
    )
    reflexo_name = serializers.CharField(source='reflexo.name', read_only=True)

    # Campo calculado
    appointments_count = serializers.ReadOnlyField()
    
    class Meta:
        model = AppointmentStatus
        fields = [
            'id',
            'reflexo_id', 'reflexo_name',
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
        # Limitar por tenant: si admin y envía reflexo_id, validar en ese tenant; sino usar tenant del usuario
        req = self.context.get('request')
        tenant_id = None
        if req is not None and req.user is not None:
            if is_global_admin(req.user):
                # usar el reflexo_id enviado si está disponible
                provided = (self.initial_data or {}).get('reflexo_id')
                tenant_id = int(provided) if provided not in (None, '',) else get_tenant(req.user)
            else:
                tenant_id = get_tenant(req.user)
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
