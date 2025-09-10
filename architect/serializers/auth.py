from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError(_('Se requieres email y contraseña.'))

        # Django's default ModelBackend expects 'username' and 'password'.
        # If your custom user model uses a different USERNAME_FIELD (e.g., 'user_name' or 'email'),
        # the ModelBackend still expects 'username' here, and internally will map it to USERNAME_FIELD.
        user = authenticate(request=self.context.get('request'), username=email, password=password)

        if user is None:
            raise AuthenticationFailed(_('Credenciales inválidas.'))
        
        # Standard is_active check
        if not getattr(user, 'is_active', True):
            raise AuthenticationFailed(_('Cuenta no activada.'))
        
        refresh = RefreshToken.for_user(user)

        return {
            'email': user.email,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
        }


class RegisterSerializer(serializers.ModelSerializer):
    # Required account fields
    email = serializers.EmailField(required=True)
    user_name = serializers.CharField(required=True, max_length=150)
    document_number = serializers.CharField(required=True, max_length=20)
    name = serializers.CharField(required=True, max_length=100)
    paternal_lastname = serializers.CharField(required=True, max_length=100)
    maternal_lastname = serializers.CharField(required=True, max_length=100)

    # Password fields
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'user_name',
            'document_number',
            'name',
            'paternal_lastname',
            'maternal_lastname',
            'password',
            'password_confirm',
        )

    def validate_password(self, value):
        # Validación personalizada de contraseña
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Verificar que no sea una contraseña común
        common_passwords = ['password', '123456', '12345678', 'qwerty', 'abc123', 'password123', 'admin', 'letmein']
        if value.lower() in common_passwords:
            raise serializers.ValidationError("Esta contraseña es demasiado común. Elige una contraseña más segura.")
        
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden"})
        # Unicidad explícita para evitar errores 500 por IntegrityError
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Este email ya está registrado"})
        if User.objects.filter(user_name=attrs['user_name']).exists():
            raise serializers.ValidationError({"user_name": "Este nombre de usuario ya está en uso"})
        if User.objects.filter(document_number=attrs['document_number']).exists():
            raise serializers.ValidationError({"document_number": "Este número de documento ya está registrado"})
        return attrs

    def create(self, validated_data):
        try:
            validated_data.pop('password_confirm')
            user = User.objects.create_user(**validated_data)
            return user
        except IntegrityError as e:
            raise serializers.ValidationError({"error": "Error de integridad. Por favor, revise los datos ingresados."})