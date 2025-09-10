from rest_framework import serializers
from ..models.medical_record import MedicalRecord
from .patient import PatientSerializer
from .diagnosis import DiagnosisSerializer
from reflexo.models import Reflexo

class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer para el modelo MedicalRecord."""
    
    # Campos relacionados anidados
    patient = PatientSerializer(read_only=True)
    diagnose = DiagnosisSerializer(read_only=True)
    
    # IDs para escritura
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientSerializer.Meta.model.objects.filter(deleted_at__isnull=True), 
        source='patient', 
        write_only=True
    )
    diagnose_id = serializers.PrimaryKeyRelatedField(
        queryset=DiagnosisSerializer.Meta.model.objects.filter(deleted_at__isnull=True), 
        source='diagnose', 
        write_only=True
    )
    
    # Tenant (reflexo)
    reflexo_id = serializers.PrimaryKeyRelatedField(
        queryset=Reflexo.objects.all(), source='reflexo', required=False
    )
    reflexo_name = serializers.CharField(source='reflexo.name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'diagnose', 'diagnosis_date',
            'symptoms', 'treatment', 'notes', 'status',
            'patient_id', 'diagnose_id', 'reflexo_id', 'reflexo_name', 'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def validate_diagnosis_date(self, value):
        """Validar que la fecha de diagnóstico no sea futura."""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("La fecha de diagnóstico no puede ser futura.")
        return value
    
    def validate(self, data):
        """Validación personalizada.
        Soporta actualizaciones parciales: si faltan claves en `data`, usa los valores actuales de la instancia.
        """
        patient = data.get('patient') or (self.instance.patient if self.instance else None)
        diagnose = data.get('diagnose') or (self.instance.diagnose if self.instance else None)
        diagnosis_date = data.get('diagnosis_date') or (self.instance.diagnosis_date if self.instance else None)

        # Ejecutar la validación de unicidad solo cuando tengamos los 3 valores
        if patient and diagnose and diagnosis_date:
            if MedicalRecord.objects.filter(
                patient=patient,
                diagnose=diagnose,
                diagnosis_date=diagnosis_date
            ).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError(
                    "Ya existe un registro médico para este paciente con este diagnóstico en la misma fecha."
                )
        return data

    def create(self, validated_data):
        # Asegurar que siempre se guarde el tenant (reflexo)
        reflexo = validated_data.get('reflexo')
        patient = validated_data.get('patient')
        if reflexo is None and patient is not None:
            reflexo = getattr(patient, 'reflexo', None)
            if reflexo is not None:
                validated_data['reflexo'] = reflexo
        if validated_data.get('reflexo') is None:
            raise serializers.ValidationError({'reflexo_id': 'No se pudo determinar la empresa (tenant) para el historial médico.'})
        return super().create(validated_data)

class MedicalRecordListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar historiales médicos."""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    diagnose_name = serializers.CharField(source='diagnose.name', read_only=True)
    diagnose_code = serializers.CharField(source='diagnose.code', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient_name', 'diagnose_name', 'diagnose_code',
            'diagnosis_date', 'status', 'created_at'
        ]
