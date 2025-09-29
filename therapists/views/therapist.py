# -*- coding: utf-8 -*-
"""
Vistas para la aplicación de terapeutas.
Maneja las operaciones CRUD y renderizado de templates.
"""

from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from therapists.models.therapist import Therapist
from therapists.serializers.therapist import TherapistSerializer, TherapistPhotoSerializer
from architect.utils.tenant import filter_by_tenant, is_global_admin, get_tenant
from django.core.files.storage import default_storage


class TherapistViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de terapeutas.
    Incluye:
      - Filtros por estado y por región/provincia/distrito (IDs).
      - Búsqueda por campos.
      - Soft delete y restauración.
    """
    serializer_class = TherapistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "last_name_paternal",
        "last_name_maternal",
        "document_number",
        "document_type",
        "email",
        "phone",
        "address",
        # búsqueda por nombres de ubicaciones (FK)
        "region__name",
        "province__name",
        "district__name",
    ]

    def get_queryset(self):
        """
        - Usa select_related para evitar N+1 en las FKs de ubicación.
        - Filtra por activo/inactivo (param 'active').
        - Filtra opcionalmente por IDs de region/province/district.
        """
        qs = (
            Therapist.objects.select_related("region", "province", "district")
            .all()
        )
        # Tenant isolation
        qs = filter_by_tenant(qs, self.request.user, field='reflexo')

        # filtro por estado (activo por defecto)
        active = self.request.query_params.get("active", "true").lower()
        if active in ("true", "1", "yes"):
            qs = qs.filter(deleted_at__isnull=True)
        elif active in ("false", "0", "no"):
            qs = qs.filter(deleted_at__isnull=False)

        # filtros por ubicación (IDs)
        region = self.request.query_params.get("region")
        province = self.request.query_params.get("province")
        district = self.request.query_params.get("district")
        if region:
            qs = qs.filter(region_id=region)
        if province:
            qs = qs.filter(province_id=province)
        if district:
            qs = qs.filter(district_id=district)

        return qs

    def perform_create(self, serializer):
        # Asigna tenant y local_id secuencial por empresa
        from django.db import transaction
        from django.db.models import Max
        # Determinar tenant destino
        if not is_global_admin(self.request.user):
            tenant_id = getattr(self.request.user, 'reflexo_id', None)
        else:
            # Para admin, respetar lo que venga en serializer.validated_data (reflexo)
            tenant_id = serializer.validated_data.get('reflexo').id if serializer.validated_data.get('reflexo') else None

        with transaction.atomic():
            next_local = None
            if tenant_id:
                max_local = (
                    Therapist.objects.select_for_update()
                    .filter(reflexo_id=tenant_id)
                    .aggregate(m=Max('local_id'))['m']
                )
                next_local = (max_local or 0) + 1
            if not is_global_admin(self.request.user):
                serializer.save(reflexo_id=tenant_id, local_id=next_local)
            else:
                serializer.save(local_id=next_local)

    def perform_update(self, serializer):
        # Evita cambiar el tenant para usuarios no admin
        if not is_global_admin(self.request.user):
            serializer.save(reflexo_id=getattr(self.request.user, 'reflexo_id', None))
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Tratamos PUT como actualización parcial para simplificar el flujo del cliente.
        De este modo no es obligatorio enviar todos los campos requeridos, solo los que desees cambiar.
        """
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE detail: soft delete (marca deleted_at).
        """
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def hard_delete(self, request, *args, **kwargs):
        """
        DELETE detail: hard delete (elimina definitivamente de la DB).
        """
        try:
            # Obtener terapeuta sin filtros de tenant para hard delete
            therapist = Therapist.objects.get(pk=kwargs.get('pk'))
            
            # Verificar permisos de tenant antes de eliminar
            if not is_global_admin(request.user):
                tenant_id = get_tenant(request.user)
                if therapist.reflexo_id != tenant_id:
                    return Response({"detail": "No tienes permisos para eliminar este terapeuta."}, 
                                  status=status.HTTP_403_FORBIDDEN)
            
            therapist.delete()  # Hard delete
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Therapist.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def inactive(self, request):
        """
        Endpoint para obtener terapeutas inactivos.
        Respeta paginación y serializer.
        """
        queryset = self.get_queryset().filter(deleted_at__isnull=False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=["post", "patch"])
    def restore(self, request, pk=None):
        """
        Restaura un terapeuta marcándolo como activo.
        """
        # Buscar sin filtrar por deleted_at para dar feedback claro
        try:
            qs = Therapist.objects.all()
            # Aislar por tenant si no es admin global
            if not is_global_admin(request.user):
                qs = filter_by_tenant(qs, request.user, field='reflexo')
            therapist = qs.get(pk=pk)
        except Therapist.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if therapist.deleted_at is None:
            # Idempotente: si ya está activo, responder 200 con el estado actual
            return Response(self.get_serializer(therapist).data)

    def photo(self, request, pk=None):
        """
        POST  /therapists/{id}/photo/  -> sube/asigna foto (multipart JSON)
        Respeta aislamiento por tenant para usuarios no admin.
        """
        # Obtener terapeuta respetando tenant
        try:
            qs = Therapist.objects.all()
            if not is_global_admin(request.user):
                qs = filter_by_tenant(qs, request.user, field='reflexo')
            therapist = qs.get(pk=pk)
        except Therapist.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TherapistPhotoSerializer(therapist, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            # Responder con el serializer principal para incluir profile_picture_url
            return Response({
                "message": "Foto actualizada",
                "therapist": TherapistSerializer(therapist, context={"request": request}).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def photo_delete(self, request, pk=None):
        """
        DELETE /therapists/{id}/photo/delete/ -> elimina archivo físico y limpia BD
        Respeta aislamiento por tenant para usuarios no admin.
        """
        # Obtener terapeuta respetando tenant
        try:
            qs = Therapist.objects.all()
            if not is_global_admin(request.user):
                qs = filter_by_tenant(qs, request.user, field='reflexo')
            therapist = qs.get(pk=pk)
        except Therapist.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)

        name = therapist.profile_picture or ""
        if name:
            try:
                if default_storage.exists(name):
                    default_storage.delete(name)
            except Exception:
                pass
            therapist.profile_picture = None
            therapist.save(update_fields=['profile_picture', 'updated_at'])
            return Response({
                "message": "Foto eliminada definitivamente",
                "therapist": TherapistSerializer(therapist, context={"request": request}).data
            }, status=status.HTTP_200_OK)
        return Response({"message": "El terapeuta no tiene foto para eliminar"}, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    """
    Vista para renderizar la página principal de terapeutas.
    """
    return render(request, "therapists_ui.html")
