from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.user import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserListView(APIView):
    """Lista usuarios (GET /api/architect/users/)
    Requiere autenticación.
    - Superusuarios: Pueden ver todos los usuarios
    - Usuarios staff: Solo pueden ver su propio perfil
    - Usuarios normales: Acceso denegado
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Solo superusuarios pueden ver todos los usuarios
        if user.is_superuser:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Usuarios staff solo pueden ver su propio perfil
        elif user.is_staff:
            serializer = UserSerializer(user)
            return Response([serializer.data], status=status.HTTP_200_OK)
        
        # Usuarios normales no tienen acceso
        else:
            return Response(
                {"error": "No tienes permisos para acceder a esta información"}, 
                status=status.HTTP_403_FORBIDDEN
            )


class UserCreateView(APIView):
    """Crea usuario (POST /api/architect/users/create/)
    Requiere autenticación. (Se mantiene la lógica actual sin checks extra)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEditView(APIView):
    """Edita usuario (PUT/PATCH /api/architect/users/<pk>/edit/)
    Requiere autenticación.
    PUT = actualización completa
    PATCH = actualización parcial
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Usamos partial=True para no exigir campos de creación (p. ej., password)
        serializer = UserSerializer(user, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserDeleteView(APIView):
    """Eliminación DEFINITIVA de un usuario por un administrador.
    - Requiere autenticación.
    - Permiso: superuser o staff.
    - Protección: un admin no-superuser NO puede eliminar a un superuser.
    - Efecto: hard delete (delete()), no queda rastro en Admin ni en DB.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # Verificar permisos de admin
        current = request.user
        if not (getattr(current, 'is_superuser', False) or getattr(current, 'is_staff', False)):
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)

        # Obtener usuario objetivo
        try:
            target = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # No permitir que un admin no-superuser elimine a un superuser
        if getattr(target, 'is_superuser', False) and not getattr(current, 'is_superuser', False):
            return Response({"error": "No puedes eliminar a un superusuario"}, status=status.HTTP_403_FORBIDDEN)

        # Intentar borrar archivo de foto si existe (mejor limpieza)
        try:
            photo_field = getattr(target, 'photo_url', None)
            if photo_field and getattr(photo_field, 'name', None):
                photo_field.delete(save=False)
        except Exception:
            pass

        # Hard delete definitivo
        target.delete()
        return Response({"message": "Usuario eliminado definitivamente"}, status=status.HTTP_200_OK)