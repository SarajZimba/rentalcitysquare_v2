# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Sum
# from datetime import datetime
# from decimal import Decimal
# from bill.models import Bill, BillItem
# from product.models import Product, ProductionLog, ProductOpeningStock

# class ProducedItemReportView(APIView):
#     def get(self, request):
#         product_id = request.GET.get("product_id")
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")

#         if not product_id:
#             return Response({"error": "product_id is required"}, status=400)

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=404)

#         try:
#             start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
#             end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         # ------------------------------ Opening Stock ------------------------------
#         opening_in = ProductOpeningStock.objects.filter(
#             product=product,
#             entry_date=start_date_obj
#         ).aggregate(total=Sum("opening_quantity"))["total"]

#         ledger_rows = []

#         if opening_in is not None:
#             # Use the ProductOpeningStock entry
#             balance = opening_in
#             ledger_rows.append({
#                 "date": str(start_date_obj),
#                 "miti": "",
#                 "particular": "Opening Stock",
#                 "type": "Opening",
#                 "txn_no": "",
#                 "in_qty": float(opening_in),
#                 "out_qty": 0,
#                 "balance_qty": float(balance)
#             })
#         else:
#             # Fallback: Compute from ProductionLog before start_date
#             opening_in = ProductionLog.objects.filter(
#                 product=product,
#                 production_date__lt=start_date_obj
#             ).aggregate(total=Sum("quantity_produced"))["total"] or Decimal("0.00")

#             balance = opening_in
#             ledger_rows.append({
#                 "date": str(start_date_obj),
#                 "miti": "",
#                 "particular": "Opening Stock (Fallback)",
#                 "type": "Opening",
#                 "txn_no": "",
#                 "in_qty": float(opening_in),
#                 "out_qty": 0,
#                 "balance_qty": float(balance)
#             })

#         # ------------------------------ Combine Production + Sale Entries ------------------------------
#         all_entries = []

#         # Sales Entries
#         bills = Bill.objects.all()
#         if start_date_obj:
#             bills = bills.filter(transaction_date__gte=start_date_obj)
#         if end_date_obj:
#             bills = bills.filter(transaction_date__lte=end_date_obj)
#         bills = bills.prefetch_related("bill_items")

#         for bill in bills:
#             for item in bill.bill_items.filter(product=product):
#                 all_entries.append({
#                     "date": str(bill.transaction_date),
#                     "date_obj": bill.transaction_date,
#                     "miti": bill.transaction_miti or "",
#                     "particular": bill.customer_name or "Cash Sales",
#                     "type": "Sale",
#                     "txn_no": bill.invoice_number,
#                     "in_qty": 0,
#                     "out_qty": float(item.product_quantity),
#                 })

#         # Production Entries
#         production_logs = ProductionLog.objects.filter(product=product)
#         if start_date_obj:
#             production_logs = production_logs.filter(production_date__gte=start_date_obj)
#         if end_date_obj:
#             production_logs = production_logs.filter(production_date__lte=end_date_obj)

#         for prod in production_logs:
#             all_entries.append({
#                 "date": str(prod.production_date),
#                 "date_obj": prod.production_date,
#                 "miti": prod.production_nepali_date or "",
#                 "particular": "Production",
#                 "type": "Stock In",
#                 "txn_no": f"PROD-{prod.id}",
#                 "in_qty": float(prod.quantity_produced),
#                 "out_qty": 0,
#             })

#         # ------------------------------ Sort and Calculate Balance ------------------------------
#         all_entries_sorted = sorted(all_entries, key=lambda x: x["date_obj"])

#         for entry in all_entries_sorted:
#             balance += Decimal(entry["in_qty"]) - Decimal(entry["out_qty"])
#             entry["balance_qty"] = float(balance)
#             entry.pop("date_obj", None)  # Clean up before returning

#         ledger_rows += all_entries_sorted

#         return Response(ledger_rows, status=200)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from bill.models import Bill, BillItem
from product.models import Product, ProductionLog, ProductOpeningStock
from purchase.models import ImportProductPurchase, ProductPurchase


class ProducedItemReportView(APIView):
    def get(self, request):
        product_id = request.GET.get("product_id")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if not product_id:
            return Response({"error": "product_id is required"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # ------------------------------ Opening Stock ------------------------------
        opening_in = ProductOpeningStock.objects.filter(
            product=product,
            entry_date=start_date_obj
        ).aggregate(total=Sum("opening_quantity"))["total"]

        ledger_rows = []

        if opening_in is not None:
            # Use the ProductOpeningStock entry
            balance = opening_in
            ledger_rows.append({
                "date": str(start_date_obj),
                "miti": "",
                "particular": "Opening Stock",
                "type": "Opening",
                "txn_no": "",
                "in_qty": float(opening_in),
                "out_qty": 0,
                "balance_qty": float(balance)
            })
        else:
            # Fallback: Compute from ProductionLog before start_date
            opening_in = ProductionLog.objects.filter(
                product=product,
                production_date__lt=start_date_obj
            ).aggregate(total=Sum("quantity_produced"))["total"] or Decimal("0.00")

            opening_purchase = ProductPurchase.objects.filter(
                product=product,
                purchase__bill_date__lt=start_date_obj
            ).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")

            opening_import = ImportProductPurchase.objects.filter(
                product=product,
                purchase__bill_date__lt=start_date_obj
            ).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")

            opening_sale = Decimal("0.00")
            for bill in Bill.objects.filter(transaction_date__lt=start_date_obj).prefetch_related("bill_items"):
                for item in bill.bill_items.filter(product=product):
                    opening_sale += item.product_quantity

            balance = opening_in + opening_purchase + opening_import - opening_sale
            ledger_rows.append({
                "date": str(start_date_obj),
                "miti": "",
                "particular": "Opening Stock (Fallback)",
                "type": "Opening",
                "txn_no": "",
                "in_qty": float(balance),
                "out_qty": 0,
                "balance_qty": float(balance)
            })

        # ------------------------------ Combine Production + Sale Entries ------------------------------
        all_entries = []

        # Sales Entries
        bills = Bill.objects.all()
        if start_date_obj:
            bills = bills.filter(transaction_date__gte=start_date_obj)
        if end_date_obj:
            bills = bills.filter(transaction_date__lte=end_date_obj)
        bills = bills.prefetch_related("bill_items")

        for bill in bills:
            for item in bill.bill_items.filter(product=product):
                all_entries.append({
                    "date": str(bill.transaction_date),
                    "date_obj": bill.transaction_date,
                    "miti": bill.transaction_miti or "",
                    "particular": bill.customer_name or "Cash Sales",
                    "type": "Sale",
                    "txn_no": bill.invoice_number,
                    "in_qty": 0,
                    "out_qty": float(item.product_quantity),
                })

        # Local Purchases
        purchases = ProductPurchase.objects.filter(product=product)
        if start_date_obj:
            purchases = purchases.filter(purchase__bill_date__gte=start_date_obj)
        if end_date_obj:
            purchases = purchases.filter(purchase__bill_date__lte=end_date_obj)

        for pp in purchases.select_related("purchase"):
            vendor_name = pp.purchase.vendor.name if pp.purchase.vendor else ""
            all_entries.append({
                "date": str(pp.purchase.bill_date),
                "date_obj": pp.purchase.bill_date,
                "miti": "",
                "particular": vendor_name,
                "type": "Purchase",
                "txn_no": pp.purchase.bill_no,
                "in_qty": float(pp.quantity),
                "out_qty": 0,
            })

        # Import Purchases
        import_purchases = ImportProductPurchase.objects.filter(product=product)
        if start_date_obj:
            import_purchases = import_purchases.filter(purchase__bill_date__gte=start_date_obj)
        if end_date_obj:
            import_purchases = import_purchases.filter(purchase__bill_date__lte=end_date_obj)

        for ipp in import_purchases.select_related("purchase"):
            vendor_name = ipp.purchase.vendor.name if ipp.purchase.vendor else ""
            all_entries.append({
                "date": str(ipp.purchase.bill_date),
                "date_obj": ipp.purchase.bill_date,
                "miti": "",
                "particular": vendor_name + " (Import)",
                "type": "Import Purchase",
                "txn_no": ipp.purchase.bill_no,
                "in_qty": float(ipp.quantity),
                "out_qty": 0,
            })

        # Production Entries
        production_logs = ProductionLog.objects.filter(product=product)
        if start_date_obj:
            production_logs = production_logs.filter(production_date__gte=start_date_obj)
        if end_date_obj:
            production_logs = production_logs.filter(production_date__lte=end_date_obj)

        for prod in production_logs:
            all_entries.append({
                "date": str(prod.production_date),
                "date_obj": prod.production_date,
                "miti": prod.production_nepali_date or "",
                "particular": "Production",
                "type": "Stock In",
                "txn_no": f"PROD-{prod.id}",
                "in_qty": float(prod.quantity_produced),
                "out_qty": 0,
            })

        # ------------------------------ Sort and Calculate Balance ------------------------------
        all_entries_sorted = sorted(all_entries, key=lambda x: x["date_obj"])

        for entry in all_entries_sorted:
            balance += Decimal(entry["in_qty"]) - Decimal(entry["out_qty"])
            entry["balance_qty"] = float(balance)
            entry.pop("date_obj", None)  # Clean up before returning

        ledger_rows += all_entries_sorted

        return Response(ledger_rows, status=200)

