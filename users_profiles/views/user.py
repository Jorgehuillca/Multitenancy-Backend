from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

# Django Core
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import models

# Serializadores locales
from ..serializers.user import (
    UserSerializer, UserUpdateSerializer, UserProfilePhotoSerializer
)

User = get_user_model()

class UserDetailView(generics.RetrieveAPIView):
    """Vista para obtener detalles del usuario autenticado"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retorna el usuario autenticado"""
        return self.request.user

class UserUpdateView(generics.UpdateAPIView):
    """Vista para actualizar información del usuario"""
    
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retorna el usuario autenticado"""
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Actualiza la información del usuario"""
        # Tratar PUT como actualización parcial para no requerir todos los campos
        # Esto también mantiene PATCH como parcial.
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Información del usuario actualizada exitosamente',
            'user': UserSerializer(instance, context={'request': request}).data
        })

class UserProfilePhotoView(APIView):
    """Vista para gestionar la foto de perfil del usuario"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Actualiza la foto de perfil del usuario"""
        serializer = UserProfilePhotoSerializer(
            request.user,
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            # Construir una URL segura en base a MEDIA_URL y el nombre relativo
            name = request.user.photo_url.name if getattr(request.user, 'photo_url', None) else None
            photo_url = f"{settings.MEDIA_URL}{name}" if name else None
            return Response({
                'message': 'Foto de perfil actualizada exitosamente',
                'photo_url': photo_url
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Elimina la foto de perfil del usuario de forma definitiva.
        - Borra el archivo del almacenamiento (MEDIA_ROOT / storage backend)
        - Limpia el campo en la base de datos (User.photo_url = NULL)
        Resultado: no queda rastro ni en Admin ni en la DB.
        """
        photo_field = getattr(request.user, 'photo_url', None)
        if photo_field:
            # Borrar archivo físico si existe
            try:
                if photo_field.name:
                    photo_field.delete(save=False)
            except Exception:
                # Incluso si falla la eliminación del archivo, continuar limpiando la BD
                pass
            # Limpiar referencia en BD
            request.user.photo_url = None
            request.user.save(update_fields=['photo_url', 'updated_at'])
            return Response({
                'message': 'Foto de perfil eliminada definitivamente'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'No tienes una foto de perfil para eliminar'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(generics.ListAPIView):
    """Vista para buscar usuarios por nombre o username"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra usuarios según el parámetro de búsqueda y tenant"""
        from architect.utils.tenant import filter_by_tenant
        
        queryset = User.objects.filter(is_active=True)
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                models.Q(user_name__icontains=search_query) |
                models.Q(name__icontains=search_query) |
                models.Q(paternal_lastname__icontains=search_query)
            )
        
        # Filtrar por tenant del usuario autenticado
        queryset = filter_by_tenant(queryset, self.request.user)
        
        return queryset[:20]  # Limitar a 20 resultados

class UserProfileView(generics.RetrieveAPIView):
    """Vista para obtener perfil completo del usuario autenticado"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retorna el usuario autenticado"""
        return self.request.user

class UserDeleteView(APIView):
    """Vista para eliminar (soft delete) el usuario autenticado"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        """Elimina DEFINITIVAMENTE (hard delete) el usuario autenticado.
        - Borra la fila de la BD, sin dejar rastro en Admin ni en la DB.
        """
        user = request.user
        
        # Verificar que no sea superuser
        if user.is_superuser:
            return Response({
                'error': 'No se puede eliminar un superusuario'
            }, status=status.HTTP_403_FORBIDDEN)
        # Hard delete por defecto: borra definitivamente la fila
        user.delete()
        return Response({
            'message': 'Usuario eliminado definitivamente'
        }, status=status.HTTP_200_OK)
    
    def get_serializer_context(self):
        """Agrega contexto adicional al serializer"""
        context = super().get_serializer_context()
        context['public_view'] = False  # Es vista privada del usuario autenticado
        return context