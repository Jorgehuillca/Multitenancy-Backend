from rest_framework import serializers
from company_reports.models.company import CompanyData


class CompanyDataSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    has_logo = serializers.SerializerMethodField()

    class Meta:
        model = CompanyData
        fields = ['id', 'reflexo', 'company_name', 'company_logo', 'logo_url', 'has_logo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reflexo', 'created_at', 'updated_at', 'logo_url', 'has_logo']

    def get_logo_url(self, obj):
        if not obj.company_logo:
            return None
        return obj.company_logo

    def get_has_logo(self, obj):
        return bool(obj.company_logo)
        
    def get_company_logo(self, obj):
        """Retorna la URL del logo."""
        if not obj.company_logo:
            return None
        return obj.company_logo