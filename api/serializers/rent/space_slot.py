# from rest_framework import serializers
# from rent.models import SpaceSlot

# class SpaceSlotSerializer(serializers.ModelSerializer):
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
    
#     class Meta:
#         model = SpaceSlot
#         fields = [
#             'id',
#             'floor',
#             'spaceno',
#             'status',
#             'status_display',
#             'initial_nea_reading',
#             'initial_diesel_reading',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class SpaceSlotBulkUploadSerializer(serializers.Serializer):
#     file = serializers.FileField()

#     def validate_file(self, value):
#         if not value.name.lower().endswith(('.xlsx', '.xls')):
#             raise serializers.ValidationError("Only .xlsx or .xls files are supported.")
#         return value


from rest_framework import serializers
from rent.models import SpaceSlot

# class SpaceSlotSerializer(serializers.ModelSerializer):
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
    
#     class Meta:
#         model = SpaceSlot
#         fields = [
#             'id',
#             'floor',
#             'spaceno',
#             'status',
#             'status_display',
#             'initial_nea_reading',
#             'initial_diesel_reading',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']


class SpaceSlotSerializer(serializers.ModelSerializer):
    latest_nea_reading = serializers.SerializerMethodField()
    latest_diesel_reading = serializers.SerializerMethodField()
    latest_reading_month = serializers.SerializerMethodField()

    class Meta:
        model = SpaceSlot
        fields = [
            'id', 'floor', 'spaceno', 'status',
            'initial_nea_reading', 'initial_diesel_reading',
            'latest_nea_reading', 'latest_diesel_reading', 'latest_reading_month',
        ]

    def _latest_bill_rent(self, obj):
        # Populated by the view's Prefetch (to_attr='latest_bill_rent_list');
        # falls back to a live query if this serializer is ever used without it.
        if hasattr(obj, 'latest_bill_rent_list'):
            return obj.latest_bill_rent_list[0] if obj.latest_bill_rent_list else None
        return (
            obj.bill_rent_items
            .filter(is_deleted=False)
            .order_by('-bill_month')
            .first()
        )

    def get_latest_nea_reading(self, obj):
        last = self._latest_bill_rent(obj)
        return str(last.nea_current_unit) if last else str(obj.initial_nea_reading)

    def get_latest_diesel_reading(self, obj):
        last = self._latest_bill_rent(obj)
        return str(last.diesel_current_unit) if last else str(obj.initial_diesel_reading)

    def get_latest_reading_month(self, obj):
        last = self._latest_bill_rent(obj)
        return last.bill_nepali_month if last else None


class SpaceSlotBulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("Only .xlsx or .xls files are supported.")
        return value