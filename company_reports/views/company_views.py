from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView

from company_reports.models.company import CompanyData
from company_reports.serialiazers.company_serializers import CompanyDataSerializer
from company_reports.services.companay_services import (
    CompanyService,
    LogoValidationService,
    LogoFileManager,
)
from architect.utils.tenant import filter_by_tenant, assign_tenant_on_create, get_tenant


class CompanyDataViewSet(viewsets.ModelViewSet):
    """API REST pura para empresas."""
    
    queryset = CompanyData.objects.all()
    serializer_class = CompanyDataSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Restringe por tenant salvo admin global."""
        base_qs = CompanyData.objects.all()
        return filter_by_tenant(base_qs, self.request.user)

    @action(detail=True, methods=['post', 'put'])
    def upload_logo(self, request, pk=None):
        """
        POST: Sube un logo solo si la empresa no tiene uno
        PUT: Actualiza el logo existente
        """
        company = self.get_object()
        # Soportar tanto URL (company_logo) como archivo multipart
        logo_url = request.data.get('company_logo')
        logo_file = (
            request.FILES.get('logo_file')
            or request.FILES.get('photo_file')
            or request.FILES.get('company_logo')
        )

        # Si viene archivo, validarlo y guardarlo en storage
        if logo_file is not None:
            try:
                LogoValidationService.validate(logo_file)
                saved_path = LogoFileManager.save_logo_file(company.company_name or 'company', logo_file)
                logo_url = saved_path  # Guardamos la ruta relativa en DB
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Si no hay ni archivo ni URL, error
        if not logo_url:
            return Response({"error": "Se requiere la URL del logo o un archivo 'logo_file'"}, status=status.HTTP_400_BAD_REQUEST)

        # Si es POST y ya tiene logo, no permitir la subida
        if request.method == 'POST' and company.company_logo:
            return Response(
                {"error": "La empresa ya tiene un logo. Use PUT para actualizar."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            CompanyService.process_logo(company, logo_url)
            message = "Logo actualizado correctamente" if request.method == 'PUT' else "Logo subido correctamente"
            # Incluir URL absoluta y relativa para facilidad del cliente
            media_url = settings.MEDIA_URL if hasattr(settings, 'MEDIA_URL') else '/media/'
            rel_url = logo_url if str(logo_url).startswith(media_url) else f"{media_url}{str(logo_url).lstrip('/\\')}"
            abs_url = request.build_absolute_uri(rel_url)
            return Response({
                "message": message,
                "company_logo": rel_url,
                "company_logo_absolute": abs_url,
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_logo(self, request, pk=None):
        """Elimina el logo de la empresa."""
        company = self.get_object()
        CompanyService.clear_company_logo(company)
        return Response({"message": "Logo eliminado correctamente"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def store(self, request):
        """Crea o actualiza datos de la empresa."""
        data = request.data.copy()
        data = assign_tenant_on_create(data, request.user)
        tenant_id = get_tenant(request.user)
    
        try:
            company = CompanyService.store(data, tenant_id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        if not company:
            return Response({"error": "No se pudo crear/actualizar la empresa"}, 
                    status=status.HTTP_400_BAD_REQUEST)

        serializer = CompanyDataSerializer(company, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def show(self, request, pk=None):
        try:
            company = self.get_object()
            serializer = self.get_serializer(company)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Http404:
            return Response({
                'status': 'error',
                'message': 'Empresa no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """Actualiza los datos de la empresa"""
        instance = self.get_object()
        data = request.data.copy()  # Hacer una copia para poder modificar
        data['id'] = kwargs.get('pk')  # Añadir el ID para que store sepa que es una actualización
        data = assign_tenant_on_create(data, request.user)
        tenant_id = get_tenant(request.user)

        try:
            # Usar CompanyService para manejar la actualización con validación de tenant
            company = CompanyService.store(data, tenant_id)
            serializer = self.get_serializer(company)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def destroy(self, request, *args, **kwargs):
        """Sobrescribe el método destroy para retornar un mensaje de éxito"""
        try:
            instance = self.get_object()
            company_name = instance.company_name
            self.perform_destroy(instance)
            return Response({
                'status': 'success',
                'message': f'Empresa "{company_name}" eliminada correctamente'
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                'status': 'error',
                'message': 'Empresa no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

'''
def company_form_view(request):
    """Vista para el formulario de gestión de empresas"""
    return render(request, 'company/company_form.html')
    '''