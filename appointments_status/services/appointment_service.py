from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from ..models import Appointment, Ticket
from ..serializers import AppointmentSerializer
from decimal import Decimal
from datetime import datetime
from histories_configurations.models import History


class AppointmentService:
    """
    Servicio para gestionar las operaciones de citas médicas.
    Basado en la estructura actualizada del modelo.
    """
    
    @transaction.atomic
    def create(self, data):
        """
        Crea una nueva cita médica con ticket automático.
        
        Args:
            data (dict): Datos de la cita a crear
            
        Returns:
            Response: Respuesta con la cita creada o error
        """
        try:
            # Validar datos requeridos mínimos del payload
            required_fields = ['patient', 'therapist', 'appointment_date', 'hour']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'El campo {field} es requerido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            payload = dict(data)

            # Convertir patient/therapist IDs a claves *_id (evita instancias manuales)
            try:
                payload['patient_id'] = int(payload.pop('patient'))
            except (KeyError, ValueError, TypeError):
                return Response({'error': 'patient debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                therapist_val = payload.pop('therapist')
                payload['therapist_id'] = int(therapist_val) if therapist_val is not None else None
            except (ValueError, TypeError):
                return Response({'error': 'therapist debe ser un ID entero o null'}, status=status.HTTP_400_BAD_REQUEST)

            # Asegurar History: usar el provisto o crear/buscar uno para el paciente
            if 'history' in payload and payload['history']:
                # Si viene history directo, solo convertir a *_id si es int
                try:
                    payload['history_id'] = int(payload.pop('history'))
                except (ValueError, TypeError):
                    return Response({'error': 'history debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Buscar historial activo más reciente del paciente (por tenant si viene)
                tenant_id = payload.get('reflexo') or payload.get('reflexo_id')
                qs = History.active.filter(patient_id=payload['patient_id'])
                if tenant_id:
                    qs = qs.filter(reflexo_id=tenant_id)
                history = qs.order_by('-created_at').first()
                if not history:
                    # Crear uno mínimo
                    history = History.objects.create(
                        patient_id=payload['patient_id'],
                        reflexo_id=tenant_id
                    )
                payload['history_id'] = history.id

            # Normalizar appointment_date + hour a datetime válido si vienen como strings
            appt_date = payload.get('appointment_date')
            hour_val = payload.get('hour')
            try:
                # Parse fecha (YYYY-MM-DD o ISO)
                if isinstance(appt_date, str):
                    # Si ya viene con tiempo, intentar parse ISO
                    try:
                        appt_dt = datetime.fromisoformat(appt_date.replace('Z', '+00:00'))
                    except ValueError:
                        # Solo fecha
                        appt_dt = datetime.strptime(appt_date, '%Y-%m-%d')
                else:
                    appt_dt = appt_date

                # Parse hora HH:MM si es str
                if isinstance(hour_val, str):
                    hour_dt = datetime.strptime(hour_val, '%H:%M').time()
                else:
                    hour_dt = hour_val

                if appt_dt and hour_dt:
                    payload['appointment_date'] = datetime.combine(appt_dt.date(), hour_dt)
            except ValueError:
                return Response({'error': 'Formato inválido de appointment_date u hour. Use YYYY-MM-DD y HH:MM.'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear la cita
            appointment = Appointment.objects.create(**payload)
            
            # El ticket se crea automáticamente mediante el signal
            # Verificar que se creó correctamente
            try:
                ticket = Ticket.objects.get(appointment=appointment)
                serializer = AppointmentSerializer(appointment)
                return Response({
                    'message': 'Cita creada exitosamente con ticket automático',
                    'appointment': serializer.data,
                    'ticket_number': ticket.ticket_number
                }, status=status.HTTP_201_CREATED)
            except Ticket.DoesNotExist:
                return Response(
                    {'error': 'Error al crear el ticket automático'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error al crear la cita: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_by_id(self, appointment_id):
        """
        Obtiene una cita por su ID.
        
        Args:
            appointment_id (int): ID de la cita
            
        Returns:
            Response: Respuesta con la cita o error si no existe
        """
        try:
            appointment = Appointment.objects.get(id=appointment_id, deleted_at__isnull=True)
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Cita no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener la cita: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def update(self, appointment_id, data):
        """
        Actualiza una cita existente.
        
        Args:
            appointment_id (int): ID de la cita a actualizar
            data (dict): Nuevos datos de la cita
            
        Returns:
            Response: Respuesta con la cita actualizada o error
        """
        try:
            appointment = Appointment.objects.get(id=appointment_id, deleted_at__isnull=True)
            
            # Actualizar campos
            for field, value in data.items():
                if hasattr(appointment, field):
                    setattr(appointment, field, value)
            
            appointment.save()
            
            # El ticket se actualiza automáticamente mediante el signal
            serializer = AppointmentSerializer(appointment)
            return Response({
                'message': 'Cita actualizada exitosamente',
                'appointment': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Cita no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al actualizar la cita: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, appointment_id):
        """
        Elimina una cita de forma definitiva (hard delete) junto con su ticket.
        """
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            # Eliminar ticket asociado si existe
            try:
                ticket = Ticket.objects.get(appointment=appointment)
                ticket.delete()
            except Ticket.DoesNotExist:
                pass
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Cita no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar la cita: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list_all(self, filters=None, pagination=None, tenant_id=None):
        """
        Lista todas las citas con filtros opcionales.
        
        Args:
            filters (dict): Filtros a aplicar
            pagination (dict): Configuración de paginación
            
        Returns:
            Response: Respuesta con la lista de citas
        """
        try:
            queryset = Appointment.objects.filter(deleted_at__isnull=True)
            if tenant_id:
                queryset = queryset.filter(reflexo_id=tenant_id)
            
            # Aplicar filtros
            if filters:
                if 'appointment_date' in filters:
                    queryset = queryset.filter(appointment_date=filters['appointment_date'])
                if 'appointment_status' in filters:
                    queryset = queryset.filter(appointment_status=filters['appointment_status'])
                if 'patient' in filters:
                    queryset = queryset.filter(patient=filters['patient'])
                if 'therapist' in filters:
                    queryset = queryset.filter(therapist=filters['therapist'])
            
            # Aplicar paginación básica
            if pagination:
                page = pagination.get('page', 1)
                page_size = pagination.get('page_size', 10)
                start = (page - 1) * page_size
                end = start + page_size
                queryset = queryset[start:end]
            
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al listar las citas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_by_date_range(self, start_date, end_date, filters=None, tenant_id=None):
        """
        Obtiene citas dentro de un rango de fechas.
        
        Args:
            start_date (date): Fecha de inicio
            end_date (date): Fecha de fin
            filters (dict): Filtros adicionales
            
        Returns:
            Response: Respuesta con las citas en el rango
        """
        try:
            # Aceptar strings 'YYYY-MM-DD' o date/datetime
            from datetime import datetime, time
            def to_date(d):
                if isinstance(d, str):
                    # Permitir ISO también
                    try:
                        return datetime.strptime(d, '%Y-%m-%d').date()
                    except ValueError:
                        # Intentar ISO (YYYY-MM-DDTHH:MM:SS)
                        return datetime.fromisoformat(d.replace('Z', '+00:00')).date()
                return getattr(d, 'date', lambda: d)() if hasattr(d, 'date') else d

            try:
                sd = to_date(start_date)
                ed = to_date(end_date)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Formato inválido. Use start_date=YYYY-MM-DD y end_date=YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Construir rango de día completo
            start_dt = datetime.combine(sd, time.min)
            end_dt = datetime.combine(ed, time.max)

            queryset = Appointment.objects.filter(
                appointment_date__range=[start_dt, end_dt],
                deleted_at__isnull=True
            )
            if tenant_id:
                queryset = queryset.filter(reflexo_id=tenant_id)
            
            # Aplicar filtros adicionales
            if filters:
                if 'appointment_status' in filters:
                    queryset = queryset.filter(appointment_status=filters['appointment_status'])
                if 'patient' in filters:
                    queryset = queryset.filter(patient=filters['patient'])
                if 'therapist' in filters:
                    queryset = queryset.filter(therapist=filters['therapist'])
            
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener citas por rango: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_completed_appointments(self, filters=None, tenant_id=None):
        """
        Obtiene las citas completadas.
        
        Args:
            filters (dict): Filtros adicionales
            
        Returns:
            Response: Respuesta con las citas completadas
        """
        try:
            today = timezone.now().date()
            queryset = Appointment.objects.filter(
                appointment_date__lt=today,
                deleted_at__isnull=True
            )
            if tenant_id:
                queryset = queryset.filter(reflexo_id=tenant_id)
            
            # Aplicar filtros adicionales
            if filters:
                if 'appointment_status' in filters:
                    queryset = queryset.filter(appointment_status=filters['appointment_status'])
                if 'patient' in filters:
                    queryset = queryset.filter(patient=filters['patient'])
                if 'therapist' in filters:
                    queryset = queryset.filter(therapist=filters['therapist'])
            
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener citas completadas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_pending_appointments(self, filters=None, tenant_id=None):
        """
        Obtiene las citas pendientes.
        
        Args:
            filters (dict): Filtros adicionales
            
        Returns:
            Response: Respuesta con las citas pendientes
        """
        try:
            today = timezone.now().date()
            queryset = Appointment.objects.filter(
                appointment_date__gte=today,
                deleted_at__isnull=True
            )
            if tenant_id:
                queryset = queryset.filter(reflexo_id=tenant_id)
            
            # Aplicar filtros adicionales
            if filters:
                if 'appointment_status' in filters:
                    queryset = queryset.filter(appointment_status=filters['appointment_status'])
                if 'patient' in filters:
                    queryset = queryset.filter(patient=filters['patient'])
                if 'therapist' in filters:
                    queryset = queryset.filter(therapist=filters['therapist'])
            
            serializer = AppointmentSerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener citas pendientes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def check_availability(self, date, hour, duration=60, tenant_id=None):
        """
        Verifica la disponibilidad para una cita.
        
        Args:
            date (date): Fecha de la cita
            hour (time): Hora de la cita
            duration (int): Duración en minutos
            
        Returns:
            Response: Respuesta con la disponibilidad
        """
        try:
            # Convertir la hora de inicio a datetime
            from datetime import datetime, timedelta
            start_datetime = datetime.combine(date, hour)
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Buscar citas que se solapen
            conflicting_appointments = Appointment.objects.filter(
                appointment_date=date,
                deleted_at__isnull=True
            ).exclude(
                hour__gte=end_datetime.time()
            ).exclude(
                hour__lte=start_datetime.time()
            )
            if tenant_id:
                conflicting_appointments = conflicting_appointments.filter(reflexo_id=tenant_id)
            
            is_available = not conflicting_appointments.exists()
            
            return Response({
                'is_available': is_available,
                'conflicting_appointments': conflicting_appointments.count() if not is_available else 0
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al verificar disponibilidad: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
