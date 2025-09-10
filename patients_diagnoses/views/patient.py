from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..models.patient import Patient
from ..serializers.patient import PatientSerializer, PatientListSerializer
from ..services.patient_service import PatientService
from architect.utils.tenant import filter_by_tenant, is_global_admin

patient_service = PatientService()

class PatientListCreateView(APIView):
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    def get(self, request):

        # Paginación opcional: si viene per_page o page, usar servicio de paginación
        if "per_page" in request.GET or "page" in request.GET:
            page_obj = patient_service.get_paginated(request)
            serializer = PatientSerializer(page_obj.object_list, many=True)
            return Response({
                "count": page_obj.paginator.count,
                "num_pages": page_obj.paginator.num_pages,
                "current_page": page_obj.number,
                "results": serializer.data,
            })
        # Aislamiento por tenant
        patients = filter_by_tenant(
            Patient.objects.filter(deleted_at__isnull=True),
            request.user,
            field='reflexo'
        )
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient, created, restored = patient_service.store_or_restore(serializer.validated_data, user=request.user)
            out = PatientSerializer(patient).data
            if created:
                return Response(out, status=status.HTTP_201_CREATED)

            # Sin soft delete en el modelo actual, tratamos como conflicto si ya existe
            return Response({"message": "El paciente ya existe", "data": out}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PatientRetrieveUpdateDeleteView(APIView):
    def get(self, request, pk):
        try:
            # Filtra por tenant
            patient = filter_by_tenant(
                Patient.objects.filter(deleted_at__isnull=True),
                request.user,
                field='reflexo'
            ).get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            patient = filter_by_tenant(
                Patient.objects.filter(deleted_at__isnull=True),
                request.user,
                field='reflexo'
            ).get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientSerializer(patient, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated = patient_service.update(patient, serializer.validated_data, user=request.user)
            return Response(PatientSerializer(updated).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Actualización parcial del paciente (solo campos enviados)."""
        try:
            patient = filter_by_tenant(
                Patient.objects.filter(deleted_at__isnull=True),
                request.user,
                field='reflexo'
            ).get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = patient_service.update(patient, serializer.validated_data, user=request.user)
            return Response(PatientSerializer(updated).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Permitir eliminación dura (hard delete) mediante query param ?hard=true
        hard_param = str(request.query_params.get('hard', '')).lower()
        hard = hard_param in ('1', 'true', 'yes')

        try:
            if hard:
                # Para hard delete, permitir eliminar incluso si ya está soft-deleted
                base_qs = Patient.all_objects.all()
                patient = filter_by_tenant(
                    base_qs,
                    request.user,
                    field='reflexo'
                ).get(pk=pk)
            else:
                # Soft delete solo sobre registros activos
                patient = filter_by_tenant(
                    Patient.objects.filter(deleted_at__isnull=True),
                    request.user,
                    field='reflexo'
                ).get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        patient_service.destroy(patient, hard=hard)
        return Response(status=status.HTTP_204_NO_CONTENT)

class PatientSearchView(APIView):
    def get(self, request):
        page_obj = patient_service.search_patients(request.GET, user=request.user)
        serializer = PatientSerializer(page_obj.object_list, many=True)
        return Response({
            "count": page_obj.paginator.count,
            "num_pages": page_obj.paginator.num_pages,
            "current_page": page_obj.number,
            "results": serializer.data,
        })

class HardDeletePatientView(APIView):
    """Endpoint dedicado para eliminación permanente de un paciente.
    URL: /api/patients/patients/<id>/hard-delete/
    """
    def delete(self, request, pk):
        try:
            # Usar all_objects para permitir borrar aunque esté soft-deleted
            base_qs = Patient.all_objects.all()
            patient = filter_by_tenant(
                base_qs,
                request.user,
                field='reflexo'
            ).get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        patient_service.destroy(patient, hard=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.