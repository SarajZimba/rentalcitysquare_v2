# serializers.py
from decimal import Decimal
from rest_framework import serializers

class PartyPaymentItemSerializer(serializers.Serializer):
    ledger_id = serializers.IntegerField()          # Cash / Card / Mobile ledger pk
    amount = serializers.DecimalField(max_digits=14, decimal_places=2,
                                      min_value=Decimal('0.01'))

class PartyPaymentJournalSerializer(serializers.Serializer):
    customer_ledger_id = serializers.CharField()    # AccountLedger.idcredit (namespaced string)
    datetime = serializers.CharField()
    user = serializers.CharField()
    particular = serializers.CharField(required=False, allow_blank=True, default='')
    bill_id = serializers.CharField(required=False, allow_blank=True, default='')
    payments = PartyPaymentItemSerializer(many=True, allow_empty=False)