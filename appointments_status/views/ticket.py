from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Ticket
from ..serializers import TicketSerializer
from ..services import TicketService
from architect.utils.tenant import (
    filter_by_tenant,
    assign_tenant_on_create,
    is_global_admin,
)


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los tickets.
    Basado en la estructura del módulo Laravel 05_appointments_status.
    """
    
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'ticket_number', 
        'payment_method', 
        'status', 
        'is_active'
    ]
    search_fields = [
        'ticket_number', 
        'description'
    ]
    ordering_fields = [
        'payment_date', 
        'amount', 
        'created_at', 
        'updated_at'
    ]
    ordering = ['-payment_date']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TicketService()
    
    def get_queryset(self):
        """
        Filtra el queryset según los parámetros de la request.
        """
        queryset = Ticket.objects.all()
        # Aislamiento por tenant
        queryset = filter_by_tenant(queryset, self.request.user, field='reflexo')
        
        # Filtros adicionales
        payment_date = self.request.query_params.get('payment_date', None)
        if payment_date:
            queryset = queryset.filter(payment_date__date=payment_date)
        
        # TODO: (Dependencia externa) - Agregar filtros cuando estén disponibles:
        # appointment_id = self.request.query_params.get('appointment_id', None)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo ticket.
        """
        payload = assign_tenant_on_create(request.data, request.user, field='reflexo')
        return self.service.create(payload, user=request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un ticket existente.
        """
        ticket_id = kwargs.get('pk')
        # Asegurar pertenencia al tenant
        try:
            _ = self.get_queryset().get(pk=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return self.service.update(ticket_id, request.data, user=request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un ticket (soft delete).
        """
        ticket_id = kwargs.get('pk')
        # Asegurar pertenencia al tenant
        try:
            _ = self.get_queryset().get(pk=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return self.service.delete(ticket_id, user=request.user)
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos los tickets con filtros y paginación.
        """
        filters = {}
        pagination = {}
        
        # Extraer filtros de query params
        for field in ['status', 'payment_method', 'appointment']:
            value = request.query_params.get(field)
            if value:
                filters[field] = value
        
        # Extraer parámetros de paginación
        page = request.query_params.get('page')
        page_size = request.query_params.get('page_size')
        if page or page_size:
            pagination['page'] = int(page) if page else 1
            pagination['page_size'] = int(page_size) if page_size else 10
        
        return self.service.list_all(filters, pagination, user=request.user)
    
    @action(detail=False, methods=['get'])
    def paid(self, request):
        """
        Obtiene los tickets pagados.
        """
        filters = {}
        for field in ['payment_method', 'appointment']:
            value = request.query_params.get(field)
            if value:
                filters[field] = value
        
        return self.service.get_paid_tickets(filters, user=request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Obtiene los tickets pendientes.
        """
        filters = {}
        for field in ['payment_method', 'appointment']:
            value = request.query_params.get(field)
            if value:
                filters[field] = value
        
        return self.service.get_pending_tickets(filters, user=request.user)
    
    @action(detail=False, methods=['get'])
    def cancelled(self, request):
        """
        Obtiene los tickets cancelados.
        """
        queryset = self.get_queryset().filter(status='cancelled')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Marca un ticket como pagado.
        """
        ticket_id = pk
        return self.service.mark_as_paid(ticket_id)
    
    @action(detail=True, methods=['post'], url_path='mark_paid')
    def mark_paid(self, request, pk=None):
        """
        Alias de mark_as_paid para compatibilidad con clientes.
        """
        ticket_id = pk
        return self.service.mark_as_paid(ticket_id)
    
    @action(detail=True, methods=['post'])
    def mark_as_cancelled(self, request, pk=None):
        """
        Marca un ticket como cancelado.
        """
        ticket_id = pk
        return self.service.mark_as_cancelled(ticket_id)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Alias de mark_as_cancelled para compatibilidad con clientes.
        """
        ticket_id = pk
        return self.service.mark_as_cancelled(ticket_id)
    
    @action(detail=False, methods=['get'])
    def by_payment_method(self, request):
        """
        Obtiene tickets agrupados por método de pago.
        """
        payment_method = request.query_params.get('payment_method') or request.query_params.get('method')
        if not payment_method:
            return Response(
                {'error': 'Se requiere payment_method (o alias: method)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        filters = {'payment_method': payment_method}
        return self.service.list_all(filters, user=request.user)
    
    @action(detail=False, methods=['get'])
    def by_ticket_number(self, request):
        """
        Obtiene un ticket por su número.
        """
        ticket_number = request.query_params.get('ticket_number')
        if not ticket_number:
            return Response(
                {'error': 'Se requiere ticket_number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return self.service.get_by_ticket_number(ticket_number, user=request.user)

    @action(detail=False, methods=['get'], url_path='by_number')
    def by_number(self, request):
        """
        Alias para obtener ticket por número usando el parámetro 'number'.
        """
        ticket_number = request.query_params.get('number') or request.query_params.get('ticket_number')
        if not ticket_number:
            return Response(
                {'error': 'Se requiere number (o alias: ticket_number)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.service.get_by_ticket_number(ticket_number, user=request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Obtiene estadísticas de tickets.
        """
        base_qs = filter_by_tenant(Ticket.objects.all(), request.user, field='reflexo')
        total_tickets = base_qs.count()
        paid_tickets = base_qs.filter(status='paid').count()
        pending_tickets = base_qs.filter(status='pending').count()
        cancelled_tickets = base_qs.filter(status='cancelled').count()
        
        # Calcular montos totales
        from django.db.models import Sum
        total_amount = Ticket.objects.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        stats = {
            'total_tickets': total_tickets,
            'paid_tickets': paid_tickets,
            'pending_tickets': pending_tickets,
            'cancelled_tickets': cancelled_tickets,
            'paid_percentage': (paid_tickets / total_tickets * 100) if total_tickets > 0 else 0,
            'total_amount_paid': float(total_amount),
        }
        
        return Response(stats)
