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
        """
        queryset = AppointmentStatus.objects.all()
        # Aislamiento por tenant
        queryset = filter_by_tenant(queryset, self.request.user, field='reflexo')
        
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
        # Asignar el tenant del usuario al crear
        from architect.utils.tenant import get_tenant, is_global_admin
        tenant_id = get_tenant(self.request.user)
        serializer.save(reflexo_id=tenant_id)

    def perform_update(self, serializer):
        # Evitar que no-admin cambie de tenant
        from architect.utils.tenant import is_global_admin, get_tenant
        data = dict(serializer.validated_data)
        if not is_global_admin(self.request.user):
            data.pop('reflexo', None)
            data.pop('reflexo_id', None)
            serializer.save(**data)
        else:
            serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Hard delete (global): elimina definitivamente el estado de cita.
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Obtiene solo los estados activos.
        """
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activa un estado de cita.
        """
        status_obj = self.get_object()
        status_obj.is_active = True
        status_obj.save()
        serializer = self.get_serializer(status_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactiva un estado de cita.
        """
        status_obj = self.get_object()
        status_obj.is_active = False
        status_obj.save()
        serializer = self.get_serializer(status_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """
        Obtiene las citas asociadas a un estado específico.
        """
        status_obj = self.get_object()
        appointments = status_obj.appointment_set.all()
        
        # TODO: (Dependencia externa) - Usar el serializer de Appointment cuando esté disponible
        from ..serializers import AppointmentSerializer
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
