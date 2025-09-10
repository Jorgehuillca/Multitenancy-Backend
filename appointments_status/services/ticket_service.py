from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from ..models import Ticket, Appointment
from architect.utils.tenant import filter_by_tenant, is_global_admin, get_tenant
from ..serializers import TicketSerializer
from django.utils import timezone
import re


class TicketService:
    """
    Servicio para gestionar las operaciones de tickets.
    Basado en la estructura del módulo Laravel 05_appointments_status.
    """
    
    @transaction.atomic
    def create(self, data, user=None):
        """
        Crea un nuevo ticket.
        
        Args:
            data (dict): Datos del ticket a crear
            
        Returns:
            Response: Respuesta con el ticket creado o error
        """
        try:
            # Validar datos requeridos
            required_fields = ['appointment', 'amount', 'payment_method']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'El campo {field} es requerido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            payload = dict(data)

            # Generar número de ticket único si no se proporciona
            if 'ticket_number' not in payload:
                payload['ticket_number'] = self.generate_ticket_number()

            # Convertir appointment → appointment_id (FK por ID)
            try:
                payload['appointment_id'] = int(payload.pop('appointment'))
            except (KeyError, ValueError, TypeError):
                return Response({'error': 'appointment debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)

            # Validar que la cita exista y (si aplica) pertenezca al mismo tenant
            try:
                appt = Appointment.objects.get(id=payload['appointment_id'])
            except Appointment.DoesNotExist:
                return Response({'error': 'La cita (appointment) no existe'}, status=status.HTTP_400_BAD_REQUEST)

            # Validación de tenant: un usuario no admin solo puede crear tickets para citas de su tenant
            if user and not is_global_admin(user):
                tenant_id = get_tenant(user)
                if appt.reflexo_id and appt.reflexo_id != tenant_id:
                    return Response({'error': 'La cita no pertenece a tu tenant'}, status=status.HTTP_403_FORBIDDEN)

            # Normalizar amount a decimal positivo
            try:
                amt = payload.get('amount', None)
                if amt is None:
                    return Response({'error': 'amount es requerido'}, status=status.HTTP_400_BAD_REQUEST)
                payload['amount'] = float(amt)
                if payload['amount'] <= 0:
                    return Response({'error': 'amount debe ser mayor a 0'}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({'error': 'amount debe ser numérico'}, status=status.HTTP_400_BAD_REQUEST)

            # Normalizar payment_method (aceptar alias en inglés → español)
            method = str(payload.get('payment_method', '')).lower()
            aliases = {
                'cash': 'efectivo',
                'card': 'tarjeta',
                'transfer': 'transferencia',
                'check': 'cheque',
                'cheque': 'cheque',
                'efectivo': 'efectivo',
                'tarjeta': 'tarjeta',
                'transferencia': 'transferencia',
                'otro': 'otro',
                'other': 'otro',
            }
            payload['payment_method'] = aliases.get(method, method)

            # Aislar por tenant: si viene user, forzar reflexo
            if user and not is_global_admin(user):
                payload['reflexo_id'] = get_tenant(user)

            try:
                ticket = Ticket.objects.create(**payload)
            except Exception as db_exc:
                # Errores de integridad / FK -> responder 400 en vez de 500
                return Response({'error': f'No se pudo crear el ticket: {str(db_exc)}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = TicketSerializer(ticket)
            
            return Response({
                'message': 'Ticket creado exitosamente',
                'ticket': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error al crear el ticket: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_by_id(self, ticket_id, user=None):
        """
        Obtiene un ticket por su ID.
        
        Args:
            ticket_id (int): ID del ticket
            
        Returns:
            Response: Respuesta con el ticket o error si no existe
        """
        try:
            qs = Ticket.objects.filter(is_active=True)
            if user:
                qs = filter_by_tenant(qs, user, field='reflexo')
            ticket = qs.get(id=ticket_id)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener el ticket: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def update(self, ticket_id, data, user=None):
        """
        Actualiza un ticket existente.
        
        Args:
            ticket_id (int): ID del ticket a actualizar
            data (dict): Nuevos datos del ticket
            
        Returns:
            Response: Respuesta con el ticket actualizado o error
        """
        try:
            qs = Ticket.objects.filter(is_active=True)
            if user:
                qs = filter_by_tenant(qs, user, field='reflexo')
            ticket = qs.get(id=ticket_id)
            
            # Actualizar campos
            for field, value in data.items():
                if hasattr(ticket, field):
                    setattr(ticket, field, value)
            
            ticket.save()
            serializer = TicketSerializer(ticket)
            
            return Response({
                'message': 'Ticket actualizado exitosamente',
                'ticket': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar el ticket: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, ticket_id, user=None):
        """
        Elimina un ticket de forma definitiva (hard delete).
        """
        try:
            qs = Ticket.objects.all()
            if user:
                qs = filter_by_tenant(qs, user, field='reflexo')
            ticket = qs.get(id=ticket_id)
            ticket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar el ticket: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list_all(self, filters=None, pagination=None, user=None):
        """
        Lista todos los tickets con filtros opcionales.
        
        Args:
            filters (dict): Filtros a aplicar
            pagination (dict): Configuración de paginación
            
        Returns:
            Response: Respuesta con la lista de tickets
        """
        try:
            queryset = Ticket.objects.filter(is_active=True)
            if user:
                queryset = filter_by_tenant(queryset, user, field='reflexo')
            
            # Aplicar filtros
            if filters:
                if 'status' in filters:
                    queryset = queryset.filter(status=filters['status'])
                if 'payment_method' in filters:
                    queryset = queryset.filter(payment_method=filters['payment_method'])
                if 'appointment' in filters:
                    queryset = queryset.filter(appointment=filters['appointment'])
                if 'payment_date' in filters:
                    queryset = queryset.filter(payment_date__date=filters['payment_date'])
            
            # Aplicar paginación básica
            if pagination:
                page = pagination.get('page', 1)
                page_size = pagination.get('page_size', 10)
                start = (page - 1) * page_size
                end = start + page_size
                queryset = queryset[start:end]
            
            serializer = TicketSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al listar los tickets: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_by_ticket_number(self, ticket_number, user=None):
        """
        Obtiene un ticket por su número.
        
        Args:
            ticket_number (str): Número del ticket
            
        Returns:
            Response: Respuesta con el ticket o error si no existe
        """
        try:
            qs = Ticket.objects.filter(ticket_number=ticket_number, is_active=True)
            if user:
                qs = filter_by_tenant(qs, user, field='reflexo')
            ticket = qs.get()
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener el ticket: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_paid_tickets(self, filters=None, user=None):
        """
        Obtiene los tickets pagados.
        
        Args:
            filters (dict): Filtros adicionales
            
        Returns:
            Response: Respuesta con los tickets pagados
        """
        try:
            queryset = Ticket.objects.filter(status='paid', is_active=True)
            if user:
                queryset = filter_by_tenant(queryset, user, field='reflexo')
            
            # Aplicar filtros adicionales
            if filters:
                if 'payment_method' in filters:
                    queryset = queryset.filter(payment_method=filters['payment_method'])
                if 'appointment' in filters:
                    queryset = queryset.filter(appointment=filters['appointment'])
                if 'payment_date' in filters:
                    queryset = queryset.filter(payment_date__date=filters['payment_date'])
            
            serializer = TicketSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener tickets pagados: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_pending_tickets(self, filters=None, user=None):
        """
        Obtiene los tickets pendientes.
        
        Args:
            filters (dict): Filtros adicionales
            
        Returns:
            Response: Respuesta con los tickets pendientes
        """
        try:
            queryset = Ticket.objects.filter(status='pending', is_active=True)
            if user:
                queryset = filter_by_tenant(queryset, user, field='reflexo')
            
            # Aplicar filtros adicionales
            if filters:
                if 'payment_method' in filters:
                    queryset = queryset.filter(payment_method=filters['payment_method'])
                if 'appointment' in filters:
                    queryset = queryset.filter(appointment=filters['appointment'])
                if 'payment_date' in filters:
                    queryset = queryset.filter(payment_date__date=filters['payment_date'])
            
            serializer = TicketSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener tickets pendientes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def mark_as_paid(self, ticket_id):
        """
        Marca un ticket como pagado.
        
        Args:
            ticket_id (int): ID del ticket
            
        Returns:
            Response: Respuesta de confirmación o error
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id, is_active=True)
            ticket.mark_as_paid()
            serializer = TicketSerializer(ticket)
            
            return Response({
                'message': 'Ticket marcado como pagado exitosamente',
                'ticket': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al marcar ticket como pagado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def mark_as_cancelled(self, ticket_id):
        """
        Marca un ticket como cancelado.
        
        Args:
            ticket_id (int): ID del ticket
            
        Returns:
            Response: Respuesta de confirmación o error
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id, is_active=True)
            ticket.mark_as_cancelled()
            serializer = TicketSerializer(ticket)
            
            return Response({
                'message': 'Ticket marcado como cancelado exitosamente',
                'ticket': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al marcar ticket como cancelado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generate_ticket_number(self):
        """
        Genera un número único de ticket en formato secuencial TKT-001, TKT-002, etc.
        
        Args:
            None
            
        Returns:
            str: Número de ticket único
        """
        # Obtener el último ticket creado
        last_ticket = Ticket.objects.order_by('-id').first()
        
        if last_ticket:
            # Extraer el número del último ticket
            try:
                # Buscar el patrón TKT-XXX en el número del ticket
                match = re.search(r'TKT-(\d+)', last_ticket.ticket_number)
                if match:
                    last_number = int(match.group(1))
                    next_number = last_number + 1
                else:
                    # Si no encuentra el patrón, empezar desde 1
                    next_number = 1
            except (ValueError, AttributeError):
                # Si hay algún error, empezar desde 1
                next_number = 1
        else:
            # Si no hay tickets, empezar desde 1
            next_number = 1
        
        # Formatear el número con ceros a la izquierda (ej: 001, 002, 010, 100)
        return f'TKT-{next_number:03d}'
