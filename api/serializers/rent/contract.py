# serializers.py

# api/serializers/rent/utils.py
from rent.models import BillRent

from bill.utils import get_opening_units

from rest_framework import serializers
from rent.models import Contract, Business, SpaceSlot


class ContractSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.company_name', read_only=True)
    slot_number = serializers.CharField(source='slot.spaceno', read_only=True)
    floor = serializers.CharField(source='slot.floor', read_only=True)

    nea_rate = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default=0)
    diesel_rate = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default=0)
    cam_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)

    nea_opening_unit = serializers.SerializerMethodField()
    diesel_opening_unit = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id',
            'business',
            'business_name',
            'slot',
            'slot_number',
            'contract_signed_date',
            'contract_start_date',
            'contract_end_date',
            'monthly_rent',
            'nea_rate',
            'diesel_rate',
            'cam_amount',
            'nea_opening_unit',
            'diesel_opening_unit',
            'status', 'floor'
        ]
        read_only_fields = ['id']

    def get_nea_opening_unit(self, obj):
        return str(get_opening_units(obj.slot)[0])

    def get_diesel_opening_unit(self, obj):
        return str(get_opening_units(obj.slot)[1])


# api/serializers/rent/contract.py
# from rest_framework import serializers
# from rent.models import Contract, SpaceSlot, BillRent


# class BusinessSlotSerializer(serializers.ModelSerializer):
#     """Slot info, with the specific contract that links it to the business."""
#     contract_id = serializers.IntegerField(source='id', read_only=True)
#     slot_id = serializers.IntegerField(source='slot.id', read_only=True)
#     floor = serializers.CharField(source='slot.floor', read_only=True)
#     spaceno = serializers.CharField(source='slot.spaceno', read_only=True)
#     slot_status = serializers.CharField(source='slot.status', read_only=True)
#     # slot_ = serializers.CharField(source='slot.status', read_only=True)

#     nea_opening_unit = serializers.SerializerMethodField()
#     diesel_opening_unit = serializers.SerializerMethodField()

#     class Meta:
#         model = Contract
#         fields = [
#             'contract_id',
#             'slot_id',
#             'floor',
#             'spaceno',
#             'slot_status',
#             'contract_signed_date',
#             'contract_start_date',
#             'contract_end_date',
#             'monthly_rent',
#             'nea_rate',
#             'diesel_rate',
#             'cam_amount',
#             'nea_opening_unit',      # NEW
#             'diesel_opening_unit',   # NEW
#             'status',
#         ]

#     def get_nea_opening_unit(self, obj):
#         return str(self._get_opening_units(obj.slot)[0])

#     def get_diesel_opening_unit(self, obj):
#         return str(self._get_opening_units(obj.slot)[1])

#     def _get_opening_units(self, slot):
#         """Same logic as BillRent._get_old_units() — last bill's closing, or slot's initial reading."""
#         # cache on self per-request to avoid duplicate queries if both fields are resolved
#         cache_attr = f'_opening_cache_{slot.id}'
#         if hasattr(self, cache_attr):
#             return getattr(self, cache_attr)

#         last_bill = (
#             BillRent.objects
#             .filter(slot=slot)
#             .order_by('-bill_month')
#             .first()
#         )
#         if last_bill:
#             result = (last_bill.nea_current_unit, last_bill.diesel_current_unit)
#         else:
#             result = (slot.initial_nea_reading, slot.initial_diesel_reading)

#         setattr(self, cache_attr, result)
#         return result




# api/serializers/rent/contract.py
from rest_framework import serializers
from rent.models import Contract, SpaceSlot
from bill.utils import get_opening_units


class BusinessSlotSerializer(serializers.ModelSerializer):
    """Slot info, with the specific contract that links it to the business."""
    contract_id = serializers.IntegerField(source='id', read_only=True)
    slot_id = serializers.IntegerField(source='slot.id', read_only=True)
    floor = serializers.CharField(source='slot.floor', read_only=True)
    spaceno = serializers.CharField(source='slot.spaceno', read_only=True)
    slot_status = serializers.CharField(source='slot.status', read_only=True)

    nea_opening_unit = serializers.SerializerMethodField()
    diesel_opening_unit = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'contract_id',
            'slot_id',
            'floor',
            'spaceno',
            'slot_status',
            'contract_signed_date',
            'contract_start_date',
            'contract_end_date',
            'monthly_rent',
            'nea_rate',
            'diesel_rate',
            'cam_amount',
            'nea_opening_unit',
            'diesel_opening_unit',
            'status',
        ]

    def get_nea_opening_unit(self, obj):
        return str(self._get_opening_units(obj.slot)[0])

    def get_diesel_opening_unit(self, obj):
        return str(self._get_opening_units(obj.slot)[1])

    def _get_opening_units(self, slot):
        """Thin per-request cache wrapper around bill.utils.get_opening_units."""
        cache_attr = f'_opening_cache_{slot.id}'
        if hasattr(self, cache_attr):
            return getattr(self, cache_attr)

        result = get_opening_units(slot)

        setattr(self, cache_attr, result)
        return result














































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































