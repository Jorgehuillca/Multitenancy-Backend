from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.auth import LoginSerializer, RegisterSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models.token_blocklist import TokenBlocklist


class LoginView(APIView):
    permission_classes = []  # Puedes agregar IsAuthenticated si lo deseas

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario registrado con éxito"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Revoca el JWT actual guardando su JTI en el blocklist.
    Requiere que el token venga en Authorization: Bearer <token>.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return Response({"error": "Authorization Bearer token requerido"}, status=status.HTTP_400_BAD_REQUEST)

        raw_token = auth.split(' ', 1)[1].strip()
        try:
            jwt_auth = JWTAuthentication()
            validated = jwt_auth.get_validated_token(raw_token)
            jti = validated.get('jti')
            if not jti:
                return Response({"error": "Token sin JTI"}, status=status.HTTP_400_BAD_REQUEST)
            # Idempotente: si ya existe, OK
            TokenBlocklist.objects.get_or_create(jti=jti, defaults={"user_id": request.user.id})
            return Response({"detail": "Sesión cerrada. Token revocado."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)