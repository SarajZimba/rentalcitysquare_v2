from rest_framework import serializers


class HotelBillVoidSerializer(serializers.Serializer):
    bill_no = serializers.CharField()
    bill_date = serializers.DateField()          # accepts "YYYY-MM-DD"
    fiscal_year = serializers.CharField()        # required: bill numbers can repeat across years
    reason = serializers.CharField(required=False, allow_blank=True, default="")