# # serializers.py
# from rest_framework import serializers
# from rent.models import BillRent, SpaceSlot, Contract


# class BillRentCreateSerializer(serializers.Serializer):
#     slot = serializers.PrimaryKeyRelatedField(queryset=SpaceSlot.objects.all())
#     contract = serializers.PrimaryKeyRelatedField(queryset=Contract.objects.all())
#     bill_month = serializers.DateField()
#     nea_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
#     diesel_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
#     cam_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
#     ac_electricity_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
#     payment_mode = serializers.CharField(required=False, default="Cash")

#     def validate(self, data):
#         if data['contract'].slot_id != data['slot'].id:
#             raise serializers.ValidationError("This contract does not belong to the given slot.")
#         if data['contract'].status != Contract.StatusChoices.ACTIVE:
#             raise serializers.ValidationError("Contract is not active.")

#         # normalize to the 1st of the month, regardless of what day was submitted
#         data['bill_month'] = data['bill_month'].replace(day=1)
#         return data


# class BillRentOutputSerializer(serializers.ModelSerializer):
#     slot_number = serializers.CharField(source='slot.spaceno', read_only=True)
#     business_name = serializers.CharField(source='contract.business.company_name', read_only=True)

#     class Meta:
#         model = BillRent
#         fields = [
#             'id', 'slot', 'slot_number', 'contract', 'business_name', 'bill_month',
#             'nea_old_unit', 'nea_current_unit', 'nea_unit_diff', 'nea_rate', 'nea_subtotal',
#             'diesel_old_unit', 'diesel_current_unit', 'diesel_unit_diff', 'diesel_rate', 'diesel_subtotal',
#             'cam_amount', 'ac_electricity_amount', 'rent_amount',
#             'subtotal', 'taxable_amount', 'is_taxable', 'vat_amount', 'total', 'bill',
#         ]


# # serializers.py
# from rest_framework import serializers
# from rent.models import BillRent, SpaceSlot, Contract, Business


# # class BillRentLineSerializer(serializers.Serializer):
# #     """One slot's readings within a business-wide bill."""
# #     slot = serializers.PrimaryKeyRelatedField(queryset=SpaceSlot.objects.all())
# #     bill_month = serializers.DateField()
# #     nea_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
# #     diesel_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
# #     cam_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
# #     ac_electricity_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

# #     def validate(self, data):
# #         data['bill_month'] = data['bill_month'].replace(day=1)
# #         return data

# class BillRentLineSerializer(serializers.Serializer):
#     """One slot's readings within a business-wide bill. cam_amount removed — comes from contract."""
#     slot = serializers.PrimaryKeyRelatedField(queryset=SpaceSlot.objects.all())
#     bill_month = serializers.DateField()
#     bill_nepali_month = serializers.CharField(max_length=10)
#     nea_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
#     diesel_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
#     ac_electricity_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def validate(self, data):
#         data['bill_month'] = data['bill_month'].replace(day=1)
#         return data


# class BusinessRentalBillCreateSerializer(serializers.Serializer):
#     business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())
#     payment_mode = serializers.CharField(required=False, default="Cash")
#     items = BillRentLineSerializer(many=True)

#     def validate(self, data):
#         business = data['business']
#         for item in data['items']:
#             # find the active contract for this business+slot
#             contract = Contract.objects.filter(
#                 business=business, slot=item['slot'], status=Contract.StatusChoices.ACTIVE
#             ).first()
#             if not contract:
#                 raise serializers.ValidationError(
#                     f"No active contract found for business {business.id} on slot {item['slot'].id}."
#                 )
#             item['contract'] = contract  # inject resolved contract for the view to use
#         return data

# from bill.models import Bill
# class RentalBillListSerializer(serializers.ModelSerializer):
#     business_name = serializers.CharField(source='customer_name', read_only=True)
#     items = BillRentOutputSerializer(source='rental_details', many=True, read_only=True)

#     class Meta:
#         model = Bill
#         fields = [
#             'id', 'invoice_number', 'business_name', 'customer_tax_number',
#             'transaction_date', 'payment_mode',
#             'sub_total', 'taxable_amount', 'tax_amount', 'grand_total',
#             'items',
#         ]

# class BusinessBillGroupSerializer(serializers.Serializer):
#     """One business's set of slot items — nested under 'businesses' in the request."""
#     business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())
#     payment_mode = serializers.CharField(required=False, default="Cash")
#     items = BillRentLineSerializer(many=True)

#     def validate(self, data):
#         business = data['business']
#         for item in data['items']:
#             contract = Contract.objects.filter(
#                 business=business, slot=item['slot'], status=Contract.StatusChoices.ACTIVE
#             ).first()
#             if not contract:
#                 raise serializers.ValidationError(
#                     f"No active contract found for business {business.id} on slot {item['slot'].id}."
#                 )
#             item['contract'] = contract
#         return data

# class MultiBusinessRentalBillCreateSerializer(serializers.Serializer):
#     """Top-level payload — a list of businesses, each producing its own Bill."""
#     businesses = BusinessBillGroupSerializer(many=True)


# class RentalBillDetailLookupSerializer(serializers.Serializer):
#     invoice_number = serializers.CharField(max_length=255)


# serializers.py
from rest_framework import serializers
from rent.models import BillRent, SpaceSlot, Contract


class BillRentCreateSerializer(serializers.Serializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=SpaceSlot.objects.all())
    contract = serializers.PrimaryKeyRelatedField(queryset=Contract.objects.all())
    bill_month = serializers.DateField()
    nea_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    diesel_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    cam_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    ac_electricity_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_mode = serializers.CharField(required=False, default="Cash")

    def validate(self, data):
        if data['contract'].slot_id != data['slot'].id:
            raise serializers.ValidationError("This contract does not belong to the given slot.")
        if data['contract'].status != Contract.StatusChoices.ACTIVE:
            raise serializers.ValidationError("Contract is not active.")

        # normalize to the 1st of the month, regardless of what day was submitted
        data['bill_month'] = data['bill_month'].replace(day=1)
        return data


class BillRentOutputSerializer(serializers.ModelSerializer):
    slot_number = serializers.CharField(source='slot.spaceno', read_only=True)
    business_name = serializers.CharField(source='contract.business.company_name', read_only=True)

    class Meta:
        model = BillRent
        fields = [
            'id', 'slot', 'slot_number', 'contract', 'business_name', 'bill_month',
            'nea_old_unit', 'nea_current_unit', 'nea_unit_diff', 'nea_rate', 'nea_subtotal',
            'diesel_old_unit', 'diesel_current_unit', 'diesel_unit_diff', 'diesel_rate', 'diesel_subtotal',
            'cam_amount', 'ac_electricity_amount', 'rent_amount',
            'subtotal', 'taxable_amount', 'is_taxable', 'vat_amount', 'total', 'bill',
        ]


# serializers.py
from rest_framework import serializers
from rent.models import BillRent, SpaceSlot, Contract, Business


class BillRentLineSerializer(serializers.Serializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=SpaceSlot.objects.all())
    bill_month = serializers.DateField()
    bill_nepali_month = serializers.CharField(max_length=10)
    nea_old_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    nea_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    diesel_old_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    diesel_current_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    ac_electricity_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

    def validate(self, data):
        data['bill_month'] = data['bill_month'].replace(day=1)
        return data

class BusinessRentalBillCreateSerializer(serializers.Serializer):
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())
    payment_mode = serializers.CharField(required=False, default="Cash")
    items = BillRentLineSerializer(many=True)

    def validate(self, data):
        business = data['business']
        for item in data['items']:
            # find the active contract for this business+slot
            contract = Contract.objects.filter(
                business=business, slot=item['slot'], status=Contract.StatusChoices.ACTIVE
            ).first()
            if not contract:
                raise serializers.ValidationError(
                    f"No active contract found for business {business.id} on slot {item['slot'].id}."
                )
            item['contract'] = contract  # inject resolved contract for the view to use
        return data

from bill.models import Bill
class RentalBillListSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='customer_name', read_only=True)
    items = BillRentOutputSerializer(source='rental_details', many=True, read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id', 'invoice_number', 'business_name', 'customer_tax_number',
            'transaction_date', 'payment_mode',
            'sub_total', 'taxable_amount', 'tax_amount', 'grand_total',
            'items',
        ]

class BusinessBillGroupSerializer(serializers.Serializer):
    """One business's set of slot items — nested under 'businesses' in the request."""
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())
    payment_mode = serializers.CharField(required=False, default="Cash")
    items = BillRentLineSerializer(many=True)

    def validate(self, data):
        business = data['business']
        for item in data['items']:
            contract = Contract.objects.filter(
                business=business, slot=item['slot'], status=Contract.StatusChoices.ACTIVE
            ).first()
            if not contract:
                raise serializers.ValidationError(
                    f"No active contract found for business {business.id} on slot {item['slot'].id}."
                )
            item['contract'] = contract
        return data

class MultiBusinessRentalBillCreateSerializer(serializers.Serializer):
    """Top-level payload — a list of businesses, each producing its own Bill."""
    businesses = BusinessBillGroupSerializer(many=True)


class RentalBillDetailLookupSerializer(serializers.Serializer):
    invoice_number = serializers.CharField(max_length=255)