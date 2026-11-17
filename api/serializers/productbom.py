# serializers.py
from rest_framework import serializers
from product.models import ProductBOM, Product

class ProductBOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBOM
        fields = ['id', 'parent_product', 'component_product', 'quantity']



from product.models import ProductionLog

class ProductionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLog
        fields = ['id', 'product', 'quantity_produced', 'production_date', 'note', 'production_nepali_date']
        read_only_fields = ['id']
