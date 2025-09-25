from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.permission import PermissionSerializer, RoleSerializer
from ..models.permission import Permission, Role
from ..permissions import IsAdminUser
from ..services.permission_service import RoleService


class PermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Solo admin puede escribir; lectura para autenticados
        if self.request.method in ["POST"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        created_role = RoleService.create_role(serializer.validated_data)
        output = RoleSerializer(created_role)
        return Response(output.data, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Solo admin puede escribir; lectura para autenticados
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, id):
        role = RoleService.get_role_by_id(id)
        if role is None:
            return Response({"detail": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        role = RoleService.get_role_by_id(id)
        if role is None:
            return Response({"detail": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(instance=role, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_role = RoleService.update_role(role, serializer.validated_data)
        output = RoleSerializer(updated_role)
        return Response(output.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        role = RoleService.get_role_by_id(id)
        if role is None:
            return Response({"detail": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(instance=role, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_role = RoleService.update_role(role, serializer.validated_data)
        output = RoleSerializer(updated_role)
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        role = RoleService.get_role_by_id(id)
        if role is None:
            return Response({"detail": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        RoleService.delete_role(role)
        return Response(status=status.HTTP_204_NO_CONTENT)