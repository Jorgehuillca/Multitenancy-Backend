from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.diagnosis import ( DiagnosisListAPIView, DiagnosisCreateAPIView, DiagnosisRetrieveUpdateDestroyAPIView, DiagnosisSearchAPIView )
from .views.patient import ( PatientListAPIView, PatientCreateAPIView, PatientRetrieveUpdateDeleteView, PatientSearchView, HardDeletePatientView )
from .views.medical_record import ( MedicalRecordListAPIView, MedicalRecordCreateAPIView, MedicalRecordRetrieveUpdateDestroyAPIView, PatientMedicalHistoryAPIView, DiagnosisStatisticsAPIView, HardDeleteMedicalRecordView )

# Eliminamos el router ya que usamos vistas basadas en clases
# router = DefaultRouter()
# router.register(r'patients',PatientListCreateView, basename='patient')

urlpatterns = [
     # URLs de diagnósticos
     path('diagnoses/', DiagnosisListAPIView.as_view(), name='diagnosis-list'), 
     path('diagnoses/create/', DiagnosisCreateAPIView.as_view(), name='diagnosis-create'), 
     # Ruta RESTful estándar (GET/PUT/PATCH/DELETE) por id
     path('diagnoses/<int:pk>/', DiagnosisRetrieveUpdateDestroyAPIView.as_view(), name='diagnosis-detail-main'),
     path('diagnoses/<int:pk>/delete/', DiagnosisRetrieveUpdateDestroyAPIView.as_view(),
     name='diagnosis-detail'),
     path('diagnoses/<int:pk>/edit/', DiagnosisRetrieveUpdateDestroyAPIView.as_view(),
     name='diagnosis-detail'),
     path('diagnoses/search/', DiagnosisSearchAPIView.as_view(), name='diagnosis-search'),
     
     # URLs de pacientes
     path('patients/', PatientListAPIView.as_view(), name='patient-list'),
     path('patients/create/', PatientCreateAPIView.as_view(), name='patient-create'),
     path('patients/<int:pk>/edit/', PatientRetrieveUpdateDeleteView.as_view(), name='patient-edit'),
     path('patients/<int:pk>/delete/', PatientRetrieveUpdateDeleteView.as_view(), name='patient-delete'),
     path('patients/<int:pk>/', PatientRetrieveUpdateDeleteView.as_view(), name='patient-detail'),
     path('patients/search/', PatientSearchView.as_view(), name='patient-search'),
     path('patients/<int:pk>/hard-delete/', HardDeletePatientView.as_view(), name='patient-hard-delete'),
     
     # URLs de historiales médicos
     path('medical-records/', MedicalRecordListAPIView.as_view(), name='medical-record-list'),
     path('medical-records/create/', MedicalRecordCreateAPIView.as_view(), name='medical-record-create'),
     path('medical-records/<int:pk>/edit/', MedicalRecordRetrieveUpdateDestroyAPIView.as_view(), name='medical-record-edit'),
     path('medical-records/<int:pk>/delete/', MedicalRecordRetrieveUpdateDestroyAPIView.as_view(), name='medical-record-delete'),
     path('medical-records/<int:pk>/', MedicalRecordRetrieveUpdateDestroyAPIView.as_view(), name='medical-record-detail'),
     path('medical-records/<int:pk>/hard-delete/', HardDeleteMedicalRecordView.as_view(), name='medical-record-hard-delete'),
     path('patients/<int:patient_id>/medical-history/', PatientMedicalHistoryAPIView.as_view(), name='patient-medical-history'),
     path('diagnosis-statistics/', DiagnosisStatisticsAPIView.as_view(), name='diagnosis-statistics'),
]


