from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # Write-only fields for creation
    document_number = serializers.CharField(required=True, max_length=20, write_only=True)
    name = serializers.CharField(required=True, max_length=100, write_only=True)
    paternal_lastname = serializers.CharField(required=True, max_length=100, write_only=True)
    maternal_lastname = serializers.CharField(required=True, max_length=100, write_only=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'user_name',
            'email',
            'phone',
            'account_statement',
            'is_active',
            'created_at',
            'updated_at',
            # write-only create fields
            'document_number',
            'name',
            'paternal_lastname',
            'maternal_lastname',
            'password',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Extract write-only fields for creation
        document_number = validated_data.pop('document_number')
        name = validated_data.pop('name')
        paternal_lastname = validated_data.pop('paternal_lastname')
        maternal_lastname = validated_data.pop('maternal_lastname')
        password = validated_data.pop('password')

        # Remaining fields include user_name, email, phone, account_statement, is_active
        user = User.objects.create_user(
            password=password,
            document_number=document_number,
            name=name,
            paternal_lastname=paternal_lastname,
            maternal_lastname=maternal_lastname,
            **validated_data,
        )
        return user