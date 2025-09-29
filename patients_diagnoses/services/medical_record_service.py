from django.db.models import Q
from django.core.paginator import Paginator
from ..models.medical_record import MedicalRecord
from ..serializers.medical_record import MedicalRecordSerializer, MedicalRecordListSerializer
from architect.utils.tenant import filter_by_tenant, get_tenant, is_global_admin
from ..models.patient import Patient
from ..models.diagnosis import Diagnosis

class MedicalRecordService:
    """Servicio para gestionar historiales médicos."""
    
    @staticmethod
    def get_all_medical_records(page=1, page_size=10, search=None, filters=None, user=None):
        """Obtiene todos los historiales médicos con paginación y filtros."""
        queryset = MedicalRecord.objects.filter(
            deleted_at__isnull=True,
            patient__deleted_at__isnull=True,
            diagnose__deleted_at__isnull=True,
        )
        if user is not None:
            queryset = filter_by_tenant(queryset, user, field='reflexo')
        
        # Aplicar búsqueda
        if search:
            queryset = queryset.filter(
                Q(patient__name__icontains=search) |
                Q(patient__paternal_lastname__icontains=search) |
                Q(patient__document_number__icontains=search) |
                Q(diagnose__name__icontains=search) |
                Q(diagnose__code__icontains=search) |
                Q(symptoms__icontains=search) |
                Q(treatment__icontains=search)
            )
        
        # Aplicar filtros
        if filters:
            if filters.get('patient_id'):
                queryset = queryset.filter(patient_id=filters['patient_id'])
            if filters.get('diagnose_id'):
                queryset = queryset.filter(diagnose_id=filters['diagnose_id'])
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('date_from'):
                queryset = queryset.filter(diagnosis_date__gte=filters['date_from'])
            if filters.get('date_to'):
                queryset = queryset.filter(diagnosis_date__lte=filters['date_to'])
        
        # Ordenar por fecha de diagnóstico
        queryset = queryset.order_by('-diagnosis_date', '-created_at')
        
        # Paginación
        paginator = Paginator(queryset, page_size)
        records_page = paginator.get_page(page)
        
        # Serializar
        records_data = MedicalRecordListSerializer(records_page, many=True).data
        
        return {
            'medical_records': records_data,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'has_next': records_page.has_next(),
            'has_previous': records_page.has_previous()
        }
    
    @staticmethod
    def get_medical_record_by_id(record_id, user=None):
        """Obtiene un historial médico por su ID."""
        try:
            base = MedicalRecord.objects.filter(
                id=record_id,
                deleted_at__isnull=True,
                patient__deleted_at__isnull=True,
                diagnose__deleted_at__isnull=True,
            )
            if user is not None:
                base = filter_by_tenant(base, user, field='reflexo')
            record = base.get()
            return MedicalRecordSerializer(record).data
        except MedicalRecord.DoesNotExist:
            return None
    
    @staticmethod
    def create_medical_record(record_data, user=None):
        """Crea un nuevo historial médico."""
        data = dict(record_data)
        # IDs esperados (no nombres)
        patient_id = data.get('patient') or data.get('patient_id')
        diagnose_id = data.get('diagnose') or data.get('diagnose_id')

        # Validaciones iniciales: existencia de patient y diagnose activos (no borrados)
        if not patient_id:
            return None, {'patient_id': 'Es obligatorio'}
        if not diagnose_id:
            return None, {'diagnose_id': 'Es obligatorio'}

        patient_qs = Patient.objects.filter(id=patient_id, deleted_at__isnull=True)
        diagnose_qs = Diagnosis.objects.filter(id=diagnose_id, deleted_at__isnull=True)
        patient_obj = patient_qs.first()
        diagnose_obj = diagnose_qs.first()
        if not patient_obj:
            return None, {'patient_id': 'Paciente no existe o está eliminado'}
        if not diagnose_obj:
            return None, {'diagnose_id': 'Diagnóstico no existe o está eliminado'}

        # Manejo multitenant y determinación de reflexo_id
        if user is not None:
            if is_global_admin(user):
                # Administrador global: puede enviar reflexo_id explícito.
                # Si viene, debe coincidir con patient y diagnose; si no viene, inferir del patient.
                explicit_tid = data.get('reflexo_id')
                if explicit_tid is not None:
                    try:
                        explicit_tid = int(explicit_tid)
                    except (TypeError, ValueError):
                        return None, {'reflexo_id': 'Debe ser un entero válido'}
                    if patient_obj.reflexo_id != explicit_tid or diagnose_obj.reflexo_id != explicit_tid:
                        return None, {'reflexo_id': 'Debe coincidir con el tenant del paciente y del diagnóstico'}
                    data['reflexo_id'] = explicit_tid
                else:
                    if patient_obj.reflexo_id:
                        data['reflexo_id'] = patient_obj.reflexo_id
            else:
                # Usuario de empresa: asignar/validar tenant
                tenant_id = get_tenant(user)
                if tenant_id is None and not data.get('reflexo_id'):
                    return None, {'reflexo_id': 'Debe indicar la empresa (tenant).'}
                if tenant_id and not data.get('reflexo_id'):
                    data['reflexo_id'] = tenant_id

                # Validar que patient y diagnose pertenezcan al tenant del usuario
                try:
                    filter_by_tenant(
                        Patient.objects.filter(deleted_at__isnull=True),
                        user,
                        field='reflexo'
                    ).get(pk=patient_id)
                except Patient.DoesNotExist:
                    return None, {'patient_id': 'Paciente no pertenece a tu empresa'}
                # Los diagnósticos son globales (reflexo_id: null), no necesitan validación de tenant
                # Solo verificar que existe y está activo
                try:
                    Diagnosis.objects.filter(deleted_at__isnull=True).get(pk=diagnose_id)
                except Diagnosis.DoesNotExist:
                    return None, {'diagnose_id': 'Diagnóstico no existe o está eliminado'}

        # Validación de coherencia y presencia de tenant:
        p_tid = patient_obj.reflexo_id
        d_tid = diagnose_obj.reflexo_id
        
        # Los diagnósticos son globales (d_tid puede ser null), solo validar el paciente
        if p_tid is None:
            return None, {'non_field_errors': 'El paciente debe pertenecer a una empresa (tenant) válida.'}
        
        # Si el diagnóstico tiene tenant, debe coincidir con el paciente
        if d_tid is not None and p_tid != d_tid:
            return None, {'non_field_errors': 'Paciente y diagnóstico pertenecen a diferentes empresas (tenant).'}

        # Asegurar que el registro quede asociado al tenant del paciente (o al explícito ya validado)
        if not data.get('reflexo_id'):
            data['reflexo_id'] = p_tid
        serializer = MedicalRecordSerializer(data=data)
        if serializer.is_valid():
            record = serializer.save()
            return MedicalRecordSerializer(record).data, None
        return None, serializer.errors
    
    @staticmethod
    def update_medical_record(record_id, record_data, user=None):
        """Actualiza un historial médico existente."""
        try:
            base = MedicalRecord.objects.filter(
                id=record_id,
                deleted_at__isnull=True,
                patient__deleted_at__isnull=True,
                diagnose__deleted_at__isnull=True,
            )
            if user is not None:
                base = filter_by_tenant(base, user, field='reflexo')
            record = base.get()
            serializer = MedicalRecordSerializer(record, data=record_data, partial=True)
            if serializer.is_valid():
                record = serializer.save()
                return MedicalRecordSerializer(record).data, None
            return None, serializer.errors
        except MedicalRecord.DoesNotExist:
            return None, {'error': 'Historial médico no encontrado'}
    
    @staticmethod
    def delete_medical_record(record_id, user=None, hard: bool = False):
        """Elimina un historial médico.
        - hard=False: soft delete (marca deleted_at)
        - hard=True: eliminación permanente (DELETE)
        """
        try:
            if hard:
                base = MedicalRecord.all_objects.filter(id=record_id)
            else:
                base = MedicalRecord.objects.filter(id=record_id, deleted_at__isnull=True)
            if user is not None:
                base = filter_by_tenant(base, user, field='reflexo')
            record = base.get()
            if hard:
                record.delete()
            else:
                record.soft_delete()
            return True
        except MedicalRecord.DoesNotExist:
            return False
    
    @staticmethod
    def restore_medical_record(record_id):
        """Restaura un historial médico eliminado."""
        try:
            record = MedicalRecord.objects.get(id=record_id, deleted_at__isnull=False)
            record.restore()
            return True
        except MedicalRecord.DoesNotExist:
            return False
    
    @staticmethod
    def get_patient_medical_history(patient_id, page=1, page_size=10, user=None):
        """Obtiene el historial médico de un paciente específico."""
        queryset = MedicalRecord.objects.filter(
            patient_id=patient_id,
            deleted_at__isnull=True,
            patient__deleted_at__isnull=True,
            diagnose__deleted_at__isnull=True,
        ).order_by('-diagnosis_date', '-created_at')
        if user is not None:
            queryset = filter_by_tenant(queryset, user, field='reflexo')
        
        # Paginación
        paginator = Paginator(queryset, page_size)
        records_page = paginator.get_page(page)
        
        # Serializar
        records_data = MedicalRecordListSerializer(records_page, many=True).data
        
        return {
            'medical_records': records_data,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'has_next': records_page.has_next(),
            'has_previous': records_page.has_previous()
        }
    
    @staticmethod
    def get_diagnosis_statistics(user=None):
        """Obtiene estadísticas de diagnósticos."""
        from django.db.models import Count
        
        base = MedicalRecord.objects.filter(deleted_at__isnull=True)
        if user is not None:
            base = filter_by_tenant(base, user, field='reflexo')
        stats = base.values('diagnose__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return stats
