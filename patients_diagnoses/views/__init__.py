from .patient import (
    PatientListAPIView,
    PatientCreateAPIView, 
    PatientRetrieveUpdateDeleteView, 
    PatientSearchView
)
from .diagnosis import (
    DiagnosisListAPIView,
    DiagnosisCreateAPIView, 
    DiagnosisRetrieveUpdateDestroyAPIView, 
    DiagnosisSearchAPIView
)
from .medical_record import (
    MedicalRecordListAPIView,
    MedicalRecordCreateAPIView, 
    MedicalRecordRetrieveUpdateDestroyAPIView,
    PatientMedicalHistoryAPIView,
    DiagnosisStatisticsAPIView
)

__all__ = [
    'PatientListAPIView',
    'PatientCreateAPIView', 
    'PatientRetrieveUpdateDeleteView', 
    'PatientSearchView',
    'DiagnosisListAPIView',
    'DiagnosisCreateAPIView', 
    'DiagnosisRetrieveUpdateDestroyAPIView', 
    'DiagnosisSearchAPIView',
    'MedicalRecordListAPIView',
    'MedicalRecordCreateAPIView', 
    'MedicalRecordRetrieveUpdateDestroyAPIView',
    'PatientMedicalHistoryAPIView',
    'DiagnosisStatisticsAPIView'
]
