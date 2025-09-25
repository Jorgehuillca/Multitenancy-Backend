from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # Fields that appear in both request and response
    document_number = serializers.CharField(required=True, max_length=20)
    name = serializers.CharField(required=True, max_length=100)
    paternal_lastname = serializers.CharField(required=True, max_length=100)
    maternal_lastname = serializers.CharField(required=True, max_length=100)
    sex = serializers.CharField(required=False, max_length=1, allow_blank=True, allow_null=True)
    # Write-only fields for creation
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    # Admin-only on creation (now appear in response)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'user_name',
            'email',
            'name',
            'document_number',
            'paternal_lastname',
            'maternal_lastname',
            'phone',
            'sex',
            'account_statement',
            'is_active',
            'created_at',
            'updated_at',
            # write-only create fields
            'password',
            'is_staff',
            'is_superuser',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Extract fields that need special handling
        password = validated_data.pop('password')
        # Optional admin-only flags
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)

        # Enforce permissions: only superusers can set these flags
        request = self.context.get('request') if hasattr(self, 'context') else None
        requester_is_superuser = bool(getattr(getattr(request, 'user', None), 'is_superuser', False))
        if not requester_is_superuser:
            is_staff = False
            is_superuser = False

        # Create user with all remaining fields (including name, document_number, etc.)
        user = User.objects.create_user(
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **validated_data,
        )
        return user