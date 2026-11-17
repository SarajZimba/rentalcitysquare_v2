import pytz
from datetime import datetime, timedelta
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from accounting.models import AccountChart, AccountLedger
from bill.utils import create_cumulative_ledger_accounting
from api.serializers.accounting_opening import AccountChartBulkSerializer


# class AccountChartBulkImportAPI(APIView):

#     def _get_nepal_entry_date(self):
#         nepal_tz = pytz.timezone("Asia/Kathmandu")
#         today = datetime.now().date()
#         naive_datetime = datetime.combine(today, datetime.min.time())
#         nepal_datetime = nepal_tz.localize(naive_datetime)
#         return nepal_datetime + timedelta(hours=5, minutes=45)

#     def post(self, request):
#         serializer = AccountChartBulkSerializer(data=request.data, many=True)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data

#         entry_date = self._get_nepal_entry_date()

#         created_ledgers = []
#         skipped_ledgers = []

#         with transaction.atomic():
#             for chart_item in data:
#                 account_type = chart_item['account_chart']

#                 for group_item in chart_item['groups']:
#                     group_name = group_item['group']

#                     account_chart, chart_created = AccountChart.objects.get_or_create(
#                         group=group_name,
#                         defaults={'account_type': account_type}
#                     )

#                     for ledger_item in group_item['ledgers']:
#                         ledger_name = ledger_item['ledger_name']
#                         debit = ledger_item['debit']
#                         credit = ledger_item['credit']

#                         # Skip if this ledger already exists — avoid duplicate/unique clash
#                         if AccountLedger.objects.filter(ledger_name=ledger_name).exists():
#                             skipped_ledgers.append(ledger_name)
#                             continue

#                         # Determine total_value based on normal debit/credit convention
#                         if account_type in ['Asset', 'Expense']:
#                             total_value = debit - credit
#                         else:
#                             total_value = credit - debit

#                         ledger = AccountLedger.objects.create(
#                             account_chart=account_chart,
#                             ledger_name=ledger_name,
#                             total_value=total_value,
#                             opening_count=total_value,
#                         )

#                         create_cumulative_ledger_accounting(
#                             ledger, entry_date, is_opening=True
#                         )

#                         created_ledgers.append(ledger_name)

#         return Response(
#             {
#                 "created": created_ledgers,
#                 "skipped_existing": skipped_ledgers,
#             },
#             status=status.HTTP_201_CREATED,
#         )


from bill.utils import update_cumulative_ledger_accounting, update_cumulative_ledger_accounting_opening

class AccountChartBulkImportAPI(APIView):

    def _get_nepal_entry_date(self):
        nepal_tz = pytz.timezone("Asia/Kathmandu")
        today = datetime.now().date()
        naive_datetime = datetime.combine(today, datetime.min.time())
        nepal_datetime = nepal_tz.localize(naive_datetime)
        return nepal_datetime + timedelta(hours=5, minutes=45)

    def post(self, request):
        serializer = AccountChartBulkSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        entry_date = self._get_nepal_entry_date()

        created_ledgers = []
        updated_ledgers = []

        with transaction.atomic():
            for chart_item in data:
                account_type = chart_item['account_chart']

                for group_item in chart_item['groups']:
                    group_name = group_item['group']

                    account_chart, chart_created = AccountChart.objects.get_or_create(
                        group=group_name,
                        defaults={'account_type': account_type}
                    )

                    for ledger_item in group_item['ledgers']:
                        ledger_name = ledger_item['ledger_name']
                        debit = ledger_item['debit']
                        credit = ledger_item['credit']
                        is_opening = ledger_item.get('is_opening', False)


                        print("Got this is_openieng", is_opening)
                        # Determine total_value based on normal debit/credit convention
                        if account_type in ['Asset', 'Expense']:
                            total_value = debit - credit
                        else:
                            total_value = credit - debit

                        existing_ledger = AccountLedger.objects.filter(
                            ledger_name=ledger_name
                        ).select_for_update().first()

                        if existing_ledger:
                            # print("Got this is_openieng inside existing ledger", is_opening)
                            # incoming_value = total_value
                            # existing_ledger.total_value = existing_ledger.total_value + incoming_value
                            # existing_ledger.save(update_fields=['total_value'])

                            print("Got this is_openieng inside existing ledger", is_opening)
                            incoming_value = total_value
                            existing_ledger.total_value = existing_ledger.total_value + incoming_value

                            update_fields = ['total_value']

                            if is_opening:
                                # existing_ledger.opening_count = existing_ledger.total_value
                                existing_ledger.opening_count = incoming_value
                                update_fields.append('opening_count')

                            existing_ledger.save(update_fields=update_fields)

                            update_cumulative_ledger_accounting_opening(
                                existing_ledger, entry_date, is_opening=is_opening
                            )

                            updated_ledgers.append(ledger_name)
                            continue

                        ledger = AccountLedger.objects.create(
                            account_chart=account_chart,
                            ledger_name=ledger_name,
                            total_value=total_value,
                            opening_count=0,
                        )

                        create_cumulative_ledger_accounting(
                            ledger, entry_date, is_opening=is_opening
                        )

                        created_ledgers.append(ledger_name)

        return Response(
            {
                "created": created_ledgers,
                "updated_existing": updated_ledgers,
            },
            status=status.HTTP_201_CREATED,
        )


from decimal import Decimal

from rest_framework import serializers, status
from accounting.models import CumulativeLedger
from accounting.utils import sub_below_cumulative_entries, add_below_cumulative_entries, change_date_to_datetime


class OpeningCountSerializer(serializers.Serializer):
    # mirrors OpeningCountForm's two fields
    opening_count = serializers.DecimalField(max_digits=12, decimal_places=2)
    entry_date = serializers.DateField()


class OpeningCountAPIView(APIView):
    """
    GET  /ledgers/<ledger_id>/opening-count/  -> current opening value + date
    POST /ledgers/<ledger_id>/opening-count/  -> create/edit opening entry
    Exact business logic ported from EditOpeningCountView.
    """

    def get_ledger(self, ledger_id):
        try:
            return AccountLedger.objects.get(id=ledger_id)
        except AccountLedger.DoesNotExist:
            return None

    def get(self, request, ledger_id, *args, **kwargs):
        ledger = self.get_ledger(ledger_id)
        if ledger is None:
            return Response({"error": "Ledger not found."}, status=status.HTTP_404_NOT_FOUND)

        opening_entry = CumulativeLedger.objects.filter(ledger=ledger, is_opening=True).first()

        data = {
            "ledger_name": ledger.ledger_name,
            "opening_count": Decimal('0'),
            "entry_date": None,
        }

        if opening_entry:
            is_debit_normal = ledger.account_chart.account_type in ['Asset', 'Expense']
            signed_value = (
                opening_entry.debit_amount - opening_entry.credit_amount
                if is_debit_normal else
                opening_entry.credit_amount - opening_entry.debit_amount
            )
            data["opening_count"] = signed_value
            data["entry_date"] = (
                opening_entry.entry_date.date()
                if hasattr(opening_entry.entry_date, 'date')
                else opening_entry.entry_date
            )

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, ledger_id, *args, **kwargs):
        ledger = self.get_ledger(ledger_id)
        if ledger is None:
            return Response({"error": "Ledger not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OpeningCountSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_value = Decimal(str(serializer.validated_data['opening_count']))
        entry_date_raw = serializer.validated_data['entry_date']
        entry_date = change_date_to_datetime(entry_date_raw)  # naive datetime, matches journal flow
        is_debit_normal = ledger.account_chart.account_type in ['Asset', 'Expense']

        # signed -> debit/credit, respecting the ledger's normal balance side
        if is_debit_normal:
            new_debit = new_value if new_value >= 0 else Decimal('0')
            new_credit = abs(new_value) if new_value < 0 else Decimal('0')
        else:
            new_credit = new_value if new_value >= 0 else Decimal('0')
            new_debit = abs(new_value) if new_value < 0 else Decimal('0')

        opening_entry = CumulativeLedger.objects.filter(ledger=ledger, is_opening=True).first()

        if opening_entry:
            # ---- EDIT existing opening entry ----
            old_signed_value = (
                opening_entry.debit_amount - opening_entry.credit_amount
                if is_debit_normal else
                opening_entry.credit_amount - opening_entry.debit_amount
            )
            difference = new_value - old_signed_value

            opening_entry.debit_amount = new_debit
            opening_entry.credit_amount = new_credit
            opening_entry.entry_date = entry_date
            opening_entry.value_changed = new_value
            opening_entry.total_value += difference
            opening_entry.save()

            if difference > 0:
                add_below_cumulative_entries(ledger, difference, opening_entry.id)
            elif difference < 0:
                sub_below_cumulative_entries(ledger, abs(difference), opening_entry.id)

            ledger.total_value += difference
            ledger.opening_count = new_value
            ledger.save()

        else:
            # ---- CREATE new opening entry ----
            last_entry = CumulativeLedger.objects.filter(ledger=ledger).last()
            prev_total = last_entry.total_value if last_entry else Decimal('0')
            new_total = prev_total + new_value

            CumulativeLedger.objects.create(
                ledger=ledger,
                ledger_name=ledger.ledger_name,
                account_chart=ledger.account_chart,
                entry_date=entry_date,
                is_opening=True,
                debit_amount=new_debit,
                credit_amount=new_credit,
                value_changed=new_value,
                total_value=new_total,
            )

            ledger.total_value = new_total
            ledger.opening_count = new_value
            ledger.save()

        return Response({"success": True}, status=status.HTTP_200_OK)