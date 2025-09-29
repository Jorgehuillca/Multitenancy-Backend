from django.urls import path
from .views.therapist import TherapistViewSet

# Endpoints personalizados con estructura específica
urlpatterns = [
    path('therapists/', TherapistViewSet.as_view({'get': 'list'}), name='therapist-list'),
    path('therapists/create/', TherapistViewSet.as_view({'post': 'create'}), name='therapist-create'),
    path('therapists/<int:pk>/', TherapistViewSet.as_view({'get': 'retrieve'}), name='therapist-detail'),
    path('therapists/<int:pk>/edit/', TherapistViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='therapist-edit'),
    path('therapists/<int:pk>/delete/', TherapistViewSet.as_view({'delete': 'destroy'}), name='therapist-delete'),
    path('therapists/<int:pk>/hard-delete/', TherapistViewSet.as_view({'delete': 'hard_delete'}), name='therapist-hard-delete'),
    # Endpoints para gestión de fotos
    path('therapists/<int:pk>/photo/', TherapistViewSet.as_view({'post': 'photo'}), name='therapist-photo'),
    path('therapists/<int:pk>/photo/delete/', TherapistViewSet.as_view({'delete': 'photo_delete'}), name='therapist-photo-delete'),
]