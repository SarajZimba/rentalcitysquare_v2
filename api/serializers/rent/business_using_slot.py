# serializers.py
from rest_framework import serializers
from rent.models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'id',
            'company_name',
            'pan_number',
            'contact_email',
            'contact_phone',
            'contact_person'
        ]
        read_only_fields = ['id']

    def validate_pan_number(self, value):
        return value.upper()


from rest_framework import serializers


class BusinessBulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("Only .xlsx or .xls files are supported.")
        return value