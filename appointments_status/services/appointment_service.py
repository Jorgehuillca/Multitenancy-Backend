from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from ..models import Appointment, Ticket
from patients_diagnoses.models import Patient
from therapists.models import Therapist
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
            # Ahora aceptamos patient_local_id / therapist_local_id / history_local_id con reflexo_id
            required_fields = ['appointment_date', 'hour']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'El campo {field} es requerido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            payload = dict(data)

            # Resolver por local_id si viene junto con reflexo_id
            tenant_from_payload = payload.get('reflexo_id') or payload.get('reflexo')
            try:
                tenant_from_payload = int(tenant_from_payload) if tenant_from_payload is not None else None
            except (TypeError, ValueError):
                return Response({'reflexo_id': 'Debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)

            # patient: permitir patient_local_id + reflexo_id
            if 'patient' not in payload and 'patient_id' not in payload and 'patient_local_id' in payload:
                if tenant_from_payload is None:
                    return Response({'reflexo_id': 'Requerido cuando se usa patient_local_id'}, status=status.HTTP_400_BAD_REQUEST)
                from patients_diagnoses.models import Patient as PatientModel
                p = PatientModel.objects.filter(reflexo_id=tenant_from_payload, local_id=payload['patient_local_id'], deleted_at__isnull=True).first()
                if not p:
                    return Response({'patient_local_id': 'No se encontró paciente para ese reflexo/local_id'}, status=status.HTTP_404_NOT_FOUND)
                payload['patient_id'] = p.id

            # therapist: permitir therapist_local_id + reflexo_id
            if 'therapist' not in payload and 'therapist_id' not in payload and 'therapist_local_id' in payload:
                if tenant_from_payload is None:
                    return Response({'reflexo_id': 'Requerido cuando se usa therapist_local_id'}, status=status.HTTP_400_BAD_REQUEST)
                from therapists.models import Therapist as TherapistModel
                t = TherapistModel.objects.filter(reflexo_id=tenant_from_payload, local_id=payload['therapist_local_id'], deleted_at__isnull=True).first()
                if not t:
                    return Response({'therapist_local_id': 'No se encontró terapeuta para ese reflexo/local_id'}, status=status.HTTP_404_NOT_FOUND)
                payload['therapist_id'] = t.id

            # history: permitir history_local_id + reflexo_id
            if 'history' not in payload and 'history_id' not in payload and 'history_local_id' in payload:
                if tenant_from_payload is None:
                    return Response({'reflexo_id': 'Requerido cuando se usa history_local_id'}, status=status.HTTP_400_BAD_REQUEST)
                from histories_configurations.models import History as HistoryModel
                h = HistoryModel.active.filter(reflexo_id=tenant_from_payload, local_id=payload['history_local_id']).first()
                if not h:
                    return Response({'history_local_id': 'No se encontró historial para ese reflexo/local_id'}, status=status.HTTP_404_NOT_FOUND)
                payload['history_id'] = h.id

            # Convertir patient/therapist IDs a claves *_id (evita instancias manuales)
            if 'patient_id' not in payload:
                try:
                    payload['patient_id'] = int(payload.pop('patient'))
                except (KeyError, ValueError, TypeError):
                    return Response({'error': 'patient debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)
            if 'therapist_id' not in payload:
                try:
                    therapist_val = payload.pop('therapist')
                    payload['therapist_id'] = int(therapist_val) if therapist_val is not None else None
                except (ValueError, TypeError):
                    return Response({'error': 'therapist debe ser un ID entero o null'}, status=status.HTTP_400_BAD_REQUEST)

            # Validar existencia de Patient y Therapist, y consistencia de tenant
            # Nota: Patient.objects por defecto excluye soft-deleted; Therapist no, por lo que filtramos deleted_at
            try:
                patient_id = int(payload.get('patient')) if 'patient' in payload else int(payload.get('patient_id'))
            except (TypeError, ValueError):
                return Response({'error': 'patient debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                patient_obj = Patient.objects.get(pk=patient_id)
            except Patient.DoesNotExist:
                return Response({'error': 'Paciente no encontrado o eliminado'}, status=status.HTTP_400_BAD_REQUEST)

            therapist_id_val = payload.get('therapist') if 'therapist' in payload else payload.get('therapist_id')
            therapist_obj = None
            if therapist_id_val is not None:
                try:
                    therapist_id = int(therapist_id_val)
                except (TypeError, ValueError):
                    return Response({'error': 'therapist debe ser un ID entero o null'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    therapist_obj = Therapist.objects.get(pk=therapist_id, deleted_at__isnull=True)
                except Therapist.DoesNotExist:
                    return Response({'error': 'Terapeuta no encontrado o eliminado'}, status=status.HTTP_400_BAD_REQUEST)

            patient_tenant = getattr(patient_obj, 'reflexo_id', None)
            therapist_tenant = getattr(therapist_obj, 'reflexo_id', None) if therapist_obj else None

            # Asegurar History: usar el provisto o crear/buscar uno para el paciente
            history_tenant = None
            if 'history_id' in payload:
                provided_history_id = int(payload['history_id'])
                try:
                    history = History.active.get(pk=provided_history_id)
                except History.DoesNotExist:
                    return Response({'error': 'Historial no encontrado o eliminado'}, status=status.HTTP_404_NOT_FOUND)
                if history.patient_id != payload['patient_id']:
                    return Response({'non_field_errors': ['El historial no pertenece al paciente proporcionado.']}, status=status.HTTP_400_BAD_REQUEST)
                history_tenant = getattr(history, 'reflexo_id', None)
                payload['history_id'] = history.id
            elif 'history' in payload and payload['history']:
                # Si viene history directo, validar que exista, que no esté soft-deleted, y que pertenezca al mismo paciente
                try:
                    provided_history_id = int(payload.pop('history'))
                except (ValueError, TypeError):
                    return Response({'error': 'history debe ser un ID entero'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    history = History.active.get(pk=provided_history_id)
                except History.DoesNotExist:
                    return Response({'error': 'Historial no encontrado o eliminado'}, status=status.HTTP_404_NOT_FOUND)

                if history.patient_id != payload['patient_id']:
                    return Response({'non_field_errors': ['El historial no pertenece al paciente proporcionado.']}, status=status.HTTP_400_BAD_REQUEST)

                history_tenant = getattr(history, 'reflexo_id', None)
                payload['history_id'] = history.id
            else:
                # Buscar historial activo más reciente del paciente (por tenant si viene)
                tenant_id = payload.get('reflexo_id') or payload.get('reflexo') or patient_tenant
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
                history_tenant = getattr(history, 'reflexo_id', None)

            # Determinar tenant solicitado (si admin lo envía)
            requested_tenant = payload.get('reflexo_id') or payload.get('reflexo') or tenant_from_payload
            if requested_tenant is not None:
                try:
                    requested_tenant = int(requested_tenant)
                except (TypeError, ValueError):
                    return Response({'reflexo_id': ['Debe ser un ID entero']}, status=status.HTTP_400_BAD_REQUEST)

            # Reglas de consistencia de tenants
            if therapist_obj and (patient_tenant != therapist_tenant):
                return Response({
                    'non_field_errors': ['Paciente y terapeuta pertenecen a diferentes empresas (tenant).']
                }, status=status.HTTP_400_BAD_REQUEST)

            if requested_tenant is not None:
                if patient_tenant is not None and requested_tenant != patient_tenant:
                    return Response({'reflexo_id': ['No coincide con el tenant del paciente y/o terapeuta.']}, status=status.HTTP_400_BAD_REQUEST)
                if therapist_tenant is not None and requested_tenant != therapist_tenant:
                    return Response({'reflexo_id': ['No coincide con el tenant del paciente y/o terapeuta.']}, status=status.HTTP_400_BAD_REQUEST)
                if history_tenant is not None and requested_tenant != history_tenant:
                    return Response({'reflexo_id': ['No coincide con el tenant del historial.']}, status=status.HTTP_400_BAD_REQUEST)

            # Validación de consistencia final (paciente, terapeuta e historial deben coincidir)
            tenants = [t for t in [patient_tenant, therapist_tenant, history_tenant, requested_tenant] if t is not None]
            if tenants and any(t != tenants[0] for t in tenants):
                return Response({'non_field_errors': ['Paciente, terapeuta, historial y/o tenant solicitado pertenecen a diferentes empresas (tenant).']}, status=status.HTTP_400_BAD_REQUEST)

            # Establecer tenant de la cita: prioridad al solicitado; si no, inferir de history/patient/therapist (ya consistentes)
            tenant_id = requested_tenant or history_tenant or patient_tenant or therapist_tenant
            payload['reflexo_id'] = tenant_id
            payload.pop('reflexo', None)

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

            # Crear la cita con local_id secuencial por tenant
            from django.db.models import Max
            # Nota: estamos dentro de @transaction.atomic
            next_local = None
            if payload.get('reflexo_id'):
                max_local = (
                    Appointment.objects.select_for_update()
                    .filter(reflexo_id=payload['reflexo_id'])
                    .aggregate(m=Max('local_id'))['m']
                )
                next_local = (max_local or 0) + 1
                payload['local_id'] = next_local

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

            # Construir filtros por rango. Coincidimos si:
            # - La fecha (parte date) de appointment_date cae dentro [sd, ed], o
            # - El rango [initial_date, final_date] se solapa con [sd, ed].
            from django.db.models import Q
            queryset = Appointment.objects.filter(
                Q(appointment_date__date__range=(sd, ed)) |
                Q(initial_date__isnull=False, final_date__isnull=False, initial_date__lte=ed, final_date__gte=sd) |
                Q(initial_date__isnull=False, final_date__isnull=True, initial_date__range=(sd, ed)) |
                Q(initial_date__isnull=True, final_date__isnull=False, final_date__range=(sd, ed)),
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
            # Solo citas con estado COMPLETADO
            queryset = Appointment.objects.filter(
                appointment_status__iexact='COMPLETADO',
                deleted_at__isnull=True
            )
            if tenant_id:
                queryset = queryset.filter(reflexo_id=tenant_id)
            
            # Aplicar filtros adicionales
            if filters:
                # Ignorar appointment_status para no sobreescribir COMPLETADO, pero aceptar otros filtros
                if 'patient' in filters:
                    queryset = queryset.filter(patient=filters['patient'])
                if 'therapist' in filters:
                    queryset = queryset.filter(therapist=filters['therapist'])
                if 'appointment_date' in filters:
                    queryset = queryset.filter(appointment_date=filters['appointment_date'])
            
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
            # Solo citas con estado PENDIENTE
            queryset = Appointment.objects.filter(
                appointment_status__iexact='PENDIENTE',
                deleted_at__isnull=True
            )
            if tenant_id:
                queryset = queryset.filter(reflexo_id=tenant_id)
            
            # Aplicar filtros adicionales
            if filters:
                # Ignorar appointment_status para no sobreescribir PENDIENTE, pero aceptar otros filtros
                if 'patient' in filters:
                    queryset = queryset.filter(patient=filters['patient'])
                if 'therapist' in filters:
                    queryset = queryset.filter(therapist=filters['therapist'])
                if 'appointment_date' in filters:
                    queryset = queryset.filter(appointment_date=filters['appointment_date'])
            
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
            
            # Buscar citas que se solapen (misma fecha y hora dentro del intervalo [start, end))
            conflicting_appointments = Appointment.objects.filter(
                appointment_date__date=date,
                deleted_at__isnull=True
            ).filter(
                hour__gte=start_datetime.time(),
                hour__lt=end_datetime.time()
            )
            if tenant_id:
                conflicting_appointments = conflicting_appointments.filter(reflexo_id=tenant_id)
            
            is_available = not conflicting_appointments.exists()
            
            # Armar lista de conflictos (pequeño resumen)
            conflicts = []
            if not is_available:
                for appt in conflicting_appointments.select_related('patient', 'therapist'):
                    conflicts.append({
                        'id': appt.id,
                        'patient_name': getattr(appt.patient, 'get_full_name', lambda: None)(),
                        'therapist_name': getattr(appt.therapist, 'get_full_name', lambda: None)() if appt.therapist_id else None,
                        'appointment_date': appt.appointment_date.isoformat() if appt.appointment_date else None,
                        'hour': appt.hour.strftime('%H:%M') if appt.hour else None,
                    })

            return Response({
                'is_available': is_available,
                'conflicting_appointments': conflicting_appointments.count(),
                'conflicts': conflicts
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al verificar disponibilidad: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
