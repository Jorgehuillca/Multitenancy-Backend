from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import AppointmentStatus
from ..serializers import AppointmentStatusSerializer
from architect.utils.tenant import filter_by_tenant, get_tenant, is_global_admin


class AppointmentStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los estados de citas.
    Basado en la estructura del módulo Laravel 05_appointments_status.
    """
    
    queryset = AppointmentStatus.objects.all()
    serializer_class = AppointmentStatusSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # No incluir 'is_active' aquí porque no es un campo del modelo
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Filtra el queryset según los parámetros de la request.
        GLOBAL: No usa filtrado por tenant.
        """
        queryset = AppointmentStatus.objects.all()
        
        # Filtro por estado "activo" basado en deleted_at
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            active_bool = is_active.lower() == 'true'
            if active_bool:
                queryset = queryset.filter(deleted_at__isnull=True)
            else:
                queryset = queryset.filter(deleted_at__isnull=False)
        
        return queryset

    def perform_create(self, serializer):
        # GLOBAL: No necesita asignar tenant
        serializer.save()

    def perform_update(self, serializer):
        # GLOBAL: No necesita validación de tenant
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        DELETE detail:
        - Por defecto: soft delete (marca deleted_at).
        - ?hard=true: hard delete (elimina definitivamente; no queda en DB ni Admin).
        """
        from django.utils import timezone
        instance = self.get_object()
        hard_param = str(request.query_params.get('hard', '')).lower()
        hard = hard_param in ('1', 'true', 'yes')
        if hard:
            instance.delete()
        else:
            if getattr(instance, 'deleted_at', None) is None:
                instance.deleted_at = timezone.now()
                instance.save(update_fields=['deleted_at', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Obtiene solo los estados activos (no eliminados).
        """
        from django.utils import timezone
        queryset = self.get_queryset().filter(deleted_at__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Reactiva un estado de cita (restaura del soft delete).
        """
        from django.utils import timezone
        status_obj = self.get_object()
        status_obj.deleted_at = None
        status_obj.save(update_fields=['deleted_at', 'updated_at'])
        serializer = self.get_serializer(status_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactiva un estado de cita (soft delete).
        """
        from django.utils import timezone
        status_obj = self.get_object()
        status_obj.deleted_at = timezone.now()
        status_obj.save(update_fields=['deleted_at', 'updated_at'])
        serializer = self.get_serializer(status_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """
        Obtiene las citas asociadas a un estado específico.
        """
        status_obj = self.get_object()
        appointments = status_obj.appointment_set.all()
        
        # Respuesta simplificada para evitar import circular
        appointments_data = []
        for appointment in appointments:
            appointments_data.append({
                'id': appointment.id,
                'patient_name': f"{appointment.patient.name} {appointment.patient.paternal_lastname}" if appointment.patient else None,
                'therapist_name': f"{appointment.therapist.first_name} {appointment.therapist.last_name_paternal}" if appointment.therapist else None,
                'appointment_date': appointment.appointment_date,
                'hour': appointment.hour,
                'appointment_type': appointment.appointment_type,
                'room': appointment.room,
                'created_at': appointment.created_at,
                'updated_at': appointment.updated_at,
            })
        
        return Response({
            'status': {
                'id': status_obj.id,
                'name': status_obj.name,
                'description': status_obj.description,
            },
            'appointments': appointments_data,
            'count': len(appointments_data)
        })
