from rest_framework import serializers
from user.models import Customer


class OtherBillItemInputSerializer(serializers.Serializer):
    item_name = serializers.CharField(max_length=255)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_taxable = serializers.BooleanField(default=True)

    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class OtherBillCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    payment_mode = serializers.CharField(max_length=255, default="Cash")
    discount_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0, required=False
    )

    # Bill-level totals -- now supplied by frontend (pre-discount), same as
    # item-level subtotal/vat_amount/total. Backend no longer sums items.
    sub_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    narration = serializers.CharField(max_length=255, default="Cash")

    items = OtherBillItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

class OtherBillVoidSerializer(serializers.Serializer):
    bill_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True, default="")