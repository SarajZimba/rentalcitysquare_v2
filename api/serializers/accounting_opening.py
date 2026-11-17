from rest_framework import serializers


class LedgerEntrySerializer(serializers.Serializer):
    ledger_name = serializers.CharField(max_length=200)
    debit = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_opening = serializers.BooleanField(required=False, default=False)


class GroupEntrySerializer(serializers.Serializer):
    group = serializers.CharField(max_length=100)
    ledgers = LedgerEntrySerializer(many=True)


class AccountChartBulkSerializer(serializers.Serializer):
    account_chart = serializers.CharField(max_length=100)  # this is actually account_type
    groups = GroupEntrySerializer(many=True)