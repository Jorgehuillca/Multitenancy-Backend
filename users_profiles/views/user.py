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
        """Elimina la foto de perfil del usuario"""
        if request.user.photo_url:
            request.user.photo_url = None
            request.user.save()
            return Response({
                'message': 'Foto de perfil eliminada exitosamente'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'No tienes una foto de perfil para eliminar'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(generics.ListAPIView):
    """Vista para buscar usuarios por nombre o username"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra usuarios según el parámetro de búsqueda"""
        queryset = User.objects.filter(is_active=True)
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                models.Q(user_name__icontains=search_query) |
                models.Q(name__icontains=search_query) |
                models.Q(paternal_lastname__icontains=search_query)
            )
        
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
        """Elimina el usuario autenticado (soft delete)"""
        user = request.user
        
        # Verificar que no sea superuser
        if user.is_superuser:
            return Response({
                'error': 'No se puede eliminar un superusuario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Realizar soft delete
        user.soft_delete()
        
        return Response({
            'message': 'Usuario eliminado exitosamente'
        }, status=status.HTTP_200_OK)
    
    def get_serializer_context(self):
        """Agrega contexto adicional al serializer"""
        context = super().get_serializer_context()
        context['public_view'] = False  # Es vista privada del usuario autenticado
        return context