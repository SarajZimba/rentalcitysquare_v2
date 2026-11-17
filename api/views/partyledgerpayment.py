


# views.py
from decimal import Decimal
from django.db import transaction
from rest_framework.views import APIView
from bill.utils import update_cumulative_ledger_partyledger
from api.serializers.partyledgerpayment import PartyPaymentJournalSerializer

from api.views.journal_entry import JournalPostMixin, JournalError
from accounting.models import AccountLedger, TblJournalEntry, TblCrJournalEntry, TblDrJournalEntry

from organization.models import Organization

from accounting.utils import change_date_to_datetime

def _apply_balance(ledger, amount, is_debit, entry_date, journal_entry):
    ledger_type = ledger.account_chart.account_type
    if ledger_type in ['Asset', 'Expense']:
        delta = amount if is_debit else -amount
    elif ledger_type in ['Liability', 'Revenue', 'Equity']:
        delta = -amount if is_debit else amount
    else:
        raise JournalError(f'Unknown account type for ledger {ledger.ledger_name}', 400)
        # print(f'Unknown account type for ledger {ledger.ledger_name}', 400)
    ledger.total_value = ledger.total_value + delta
    ledger.save()
    update_cumulative_ledger_partyledger(ledger, entry_date, journal_entry)


class PartyPaymentJournalAPIView(JournalPostMixin, APIView):
    """Customer / room-charge payment received: Dr Cash|Card|Mobile, Cr customer ledger.
    No subledgers."""

    @transaction.atomic()
    def _create_entry(self, raw_item):
        serializer = PartyPaymentJournalSerializer(data=raw_item)
        if not serializer.is_valid():
            raise JournalError(f"Invalid payment data: {serializer.errors}", 400)
        data = serializer.validated_data

        entry_datetime = change_date_to_datetime(data['datetime'])
        entry_date = entry_datetime.date() if entry_datetime else None
        if not entry_date:
            raise JournalError('Invalid datetime', 400)

        # one amount per payment ledger
        paid_by_ledger = {}
        for p in data['payments']:
            paid_by_ledger[p['ledger_id']] = paid_by_ledger.get(p['ledger_id'], Decimal('0')) + p['amount']
        total = sum(paid_by_ledger.values())

        # lock ledgers so concurrent payments don't overwrite total_value
        try:
            customer_ledger = AccountLedger.objects.select_for_update().get(
                idcredit=data['customer_ledger_id'])
        except AccountLedger.DoesNotExist:
            raise JournalError('Customer ledger not found', 400)

        payment_ledgers = {
            l.id: l for l in AccountLedger.objects.select_for_update().filter(
                pk__in=paid_by_ledger.keys())
        }
        missing = set(paid_by_ledger) - set(payment_ledgers)
        if missing:
            raise JournalError(f'Payment ledger(s) {sorted(missing)} not found', 400)

        particular = data['particular'] or f"Payment received from {customer_ledger.ledger_name}"
        if data['bill_id']:
            particular += f" against bill no: {data['bill_id']}"

        fiscal_year = Organization.objects.first().get_fiscal_year()
        journal_entry = TblJournalEntry.objects.create(
            employee_name=data['user'],
            journal_total=total,
            entry_date=entry_date,
            fiscal_year=fiscal_year,
        )

        # one Dr row (cash/card/mobile) + one Cr row (customer) per payment mode,
        # paidfrom_ledger = the payment ledger, same as the party ledger view
        for ledger_id, amount in paid_by_ledger.items():
            pay_ledger = payment_ledgers[ledger_id]
            TblDrJournalEntry.objects.create(
                ledger=pay_ledger, journal_entry=journal_entry, particulars=particular,
                debit_amount=amount, paidfrom_ledger=pay_ledger)
            TblCrJournalEntry.objects.create(
                ledger=customer_ledger, journal_entry=journal_entry, particulars=particular,
                credit_amount=amount, paidfrom_ledger=pay_ledger)

        # balances: each ledger updated once per journal
        for ledger_id, amount in paid_by_ledger.items():
            _apply_balance(payment_ledgers[ledger_id], amount, True, entry_date, journal_entry)
        _apply_balance(customer_ledger, total, False, entry_date, journal_entry)

        return {'message': 'Payment journal created successfully',
                'journal_entry_id': journal_entry.pk}