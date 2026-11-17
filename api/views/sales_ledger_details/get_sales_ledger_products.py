# from django.db.models import Sum, DecimalField
# from django.db.models.functions import Coalesce
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from accounting.models import AccountLedger, TblCrJournalEntry

# from bill.models import Bill, BillItem

# class LedgerProductBreakdownAPIView(APIView):
#     def get(self, request):
#         ledger_id = request.query_params.get('ledger_id')
#         start_date = request.query_params.get('start_date')  # optional
#         end_date = request.query_params.get('end_date')

#         if not ledger_id:
#             return Response({"error": "ledger_id is required"}, status=400)

#         try:
#             ledger = AccountLedger.objects.get(pk=ledger_id)
#         except (AccountLedger.DoesNotExist, ValueError):
#             return Response({"error": "Ledger not found"}, status=404)

#         # Every bill that actually credited this ledger
#         cr_entries = TblCrJournalEntry.objects.filter(ledger=ledger)
#         if start_date:
#             cr_entries = cr_entries.filter(journal_entry__entry_date__gte=start_date)
#         if end_date:
#             cr_entries = cr_entries.filter(journal_entry__entry_date__lte=end_date)

#         bill_ids = cr_entries.values_list('journal_entry__bill_id', flat=True).distinct()
#         bills = Bill.objects.filter(
#             id__in=bill_ids,
#             is_deleted=False,
#             status=True,
#         ).exclude(payment_mode__iexact='Complimentary')

#         # Item-wise breakdown across those bills — group by product id (falls back
#         # to title only if product FK is null) so typo'd titles don't fragment totals
#         breakdown = (
#             BillItem.objects
#             .filter(bill__in=bills)
#             .values('product_id', 'product_title')
#             .annotate(
#                 total_quantity=Sum('product_quantity'),
#                 total_amount=Coalesce(
#                     Sum('amount'), 0, output_field=DecimalField()
#                 ),
#             )
#             .order_by('-total_amount')
#         )

#         # Trial-balance style rows — product acts as the "sub_ledger", all credit, debit fixed at 0
#         breakdown_list = [
#             {
#                 "product_id": row["product_id"],
#                 "product_title": row["product_title"],
#                 "total_quantity": row["total_quantity"],
#                 "debit": 0,
#                 "credit": row["total_amount"],
#             }
#             for row in breakdown
#         ]
#         breakdown_sum = sum(row["credit"] for row in breakdown_list)

#         return Response({
#             "ledger_id": ledger.id,
#             "ledger_name": ledger.ledger_name,
#             "breakdown_total": breakdown_sum,
#             "products": breakdown_list,
#         })



from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from accounting.models import AccountLedger, TblCrJournalEntry, TblDrJournalEntry

from bill.models import Bill, BillItem

from rest_framework.permissions import IsAuthenticated

class LedgerProductBreakdownAPIView(APIView):



    permission_classes = [IsAuthenticated]
    def get(self, request):
        ledger_id = request.query_params.get('ledger_id')
        start_date = request.query_params.get('start_date')  # optional
        end_date = request.query_params.get('end_date')



        if not ledger_id:
            return Response({"error": "ledger_id is required"}, status=400)

        try:
            ledger = AccountLedger.objects.get(pk=ledger_id)
        except (AccountLedger.DoesNotExist, ValueError):
            return Response({"error": "Ledger not found"}, status=404)

        def bills_for_ledger(date_lt=None, date_gte=None, date_lte=None):
            """Bills whose journal credited this ledger, filtered by date window."""
            cr = TblCrJournalEntry.objects.filter(ledger=ledger)
            if date_lt:
                cr = cr.filter(journal_entry__entry_date__lt=date_lt)
            if date_gte:
                cr = cr.filter(journal_entry__entry_date__gte=date_gte)
            if date_lte:
                cr = cr.filter(journal_entry__entry_date__lte=date_lte)

            bill_ids = cr.values_list('journal_entry__bill_id', flat=True).distinct()
            return Bill.objects.filter(
                id__in=bill_ids,
                is_deleted=False,
                status=True,
            ).exclude(payment_mode__iexact='Complimentary')

        def product_breakdown(bills_qs):
            rows = (
                BillItem.objects
                .filter(bill__in=bills_qs)
                .values('product_id', 'product_title')
                .annotate(
                    total_quantity=Sum('product_quantity'),
                    total_amount=Coalesce(Sum('amount'), 0, output_field=DecimalField()),
                )
            )
            return {row['product_id']: row for row in rows}

        # ── Opening: everything strictly before start_date ──
        opening_by_product = {}
        if start_date:
            opening_bills = bills_for_ledger(date_lt=start_date)
            opening_by_product = product_breakdown(opening_bills)

        # ── Period: within start_date/end_date window ──
        period_bills = bills_for_ledger(date_gte=start_date, date_lte=end_date)
        period_by_product = product_breakdown(period_bills)

        # Union of product ids seen in either window, so a product with only
        # opening activity (no sales this period) still shows up with credit=0
        all_product_ids = set(opening_by_product) | set(period_by_product)

        breakdown_list = []
        for pid in all_product_ids:
            opening_row = opening_by_product.get(pid)
            period_row = period_by_product.get(pid)

            title = (period_row or opening_row)['product_title']
            opening_amount = opening_row['total_amount'] if opening_row else 0
            period_amount = period_row['total_amount'] if period_row else 0
            period_qty = period_row['total_quantity'] if period_row else 0

            breakdown_list.append({
                "product_id": pid,
                "product_title": title,
                "total_quantity": period_qty,
                "opening_balance": opening_amount,       # revenue: credit-only, so opening == net credit
                "debit": 0,
                "credit": period_amount,
                "closing_balance": opening_amount + period_amount,
            })

        breakdown_list.sort(key=lambda r: r["credit"], reverse=True)
        breakdown_sum = sum(row["credit"] for row in breakdown_list)
        opening_sum = sum(row["opening_balance"] for row in breakdown_list)
        closing_sum = sum(row["closing_balance"] for row in breakdown_list)

        return Response({
            "ledger_id": ledger.id,
            "ledger_name": ledger.ledger_name,
            # "opening_balance": opening_sum,
            # "period_credit": breakdown_sum,
            # "closing_balance": closing_sum,
            "breakdown_total": breakdown_sum,
            "products": breakdown_list,
        })