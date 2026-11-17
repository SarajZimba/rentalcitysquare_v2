# serializers.py
from django.db import transaction
from rest_framework import serializers

from bill.models import EstimatedBill, EstimatedBillItem
from user.models import Customer


class EstimatedBillItemInputSerializer(serializers.Serializer):
    item_name = serializers.CharField(max_length=255)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_taxable = serializers.BooleanField(default=True)

    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class EstimatedBillCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    payment_mode = serializers.CharField(max_length=255, default="Cash")
    discount_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0, required=False
    )

    sub_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    narration = serializers.CharField(max_length=255, default="Cash")

    items = EstimatedBillItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")

        bill = EstimatedBill.objects.create(**validated_data)

        EstimatedBillItem.objects.bulk_create(
            [EstimatedBillItem(bill=bill, **item) for item in items_data]
        )

        return bill


# --- Output/read serializers ---

class EstimatedBillItemOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatedBillItem
        fields = [
            "id",
            "item_name",
            "quantity",
            "rate",
            "is_taxable",
            "subtotal",
            "vat_amount",
            "total",
        ]


class EstimatedBillOutputSerializer(serializers.ModelSerializer):
    items = EstimatedBillItemOutputSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_pan = serializers.CharField(source="customer.tax_number", read_only=True)

    class Meta:
        model = EstimatedBill
        fields = [
            "id",
            "customer",
            "customer_name",
            "payment_mode",
            "discount_amount",
            "sub_total",
            "taxable_amount",
            "tax_amount",
            "grand_total",
            "narration",
            "created_at",
            "updated_at",
            "items",
            "customer_pan"
        ]


# serializers.py (add below existing ones)

class EstimatedBillUpdateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)
    payment_mode = serializers.CharField(max_length=255, required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    sub_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    taxable_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    narration = serializers.CharField(max_length=255, required=False)

    items = EstimatedBillItemInputSerializer(many=True, required=False)

    def validate_items(self, value):
        if value is not None and not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            EstimatedBillItem.objects.bulk_create(
                [EstimatedBillItem(bill=instance, **item) for item in items_data]
            )

        return instance