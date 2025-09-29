from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.permission import PermissionSerializer
from ..models.permission import Permission


class PermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


"""Las vistas de rol fueron movidas a architect.views.role con control admin-only."""