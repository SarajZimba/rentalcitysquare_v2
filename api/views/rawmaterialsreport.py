from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum
import re

from purchase.models import ProductPurchase
from bill.models import Bill, BillItem
from product.models import Product, ProductionLog, ProductBOM, ProductOpeningStock

# class RawMaterialsReportView(APIView):
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

#         # # -------------------- Opening Stock Calculation --------------------
#         # opening_purchase = ProductPurchase.objects.filter(
#         #     product=product,
#         #     purchase__bill_date__lt=start_date_obj
#         # ).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")

#         # opening_sale = Decimal("0.00")
#         # for bill in Bill.objects.filter(transaction_date__lt=start_date_obj).prefetch_related("bill_items"):
#         #     for item in bill.bill_items.filter(product=product):
#         #         opening_sale += item.product_quantity

#         # opening_consumed = Decimal("0.00")
#         # logs_before = ProductionLog.objects.filter(production_date__lt=start_date_obj)
#         # for log in logs_before:
#         #     boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
#         #     for bom in boms:
#         #         opening_consumed += Decimal(bom.quantity) * log.quantity_produced

#         # opening_qty = opening_purchase - opening_sale - opening_consumed
#         # balance = opening_qty

#         # ledger_rows = [{
#         #     "date": str(start_date_obj) if start_date_obj else "",
#         #     "miti": "",
#         #     "particular": "Opening Stock",
#         #     "type": "Opening",
#         #     "txn_no": "",
#         #     "in_qty": float(opening_qty),
#         #     "out_qty": 0,
#         #     "balance_qty": float(balance)
#         # }]
        
#         # -------------------- Opening Stock Calculation --------------------
#         opening_entry = ProductOpeningStock.objects.filter(
#             product=product,
#             entry_date=start_date_obj
#         ).aggregate(total=Sum("opening_quantity"))["total"]

#         if opening_entry is not None:
#             # Use the opening from ProductOpeningStock
#             opening_qty = opening_entry
#             balance = opening_qty

#             ledger_rows = [{
#                 "date": str(start_date_obj) if start_date_obj else "",
#                 "miti": "",
#                 "particular": "Opening Stock",
#                 "type": "Opening",
#                 "txn_no": "",
#                 "in_qty": float(opening_qty),
#                 "out_qty": 0,
#                 "balance_qty": float(balance)
#             }]
#         else:
#             # Fallback to calculate opening
#             opening_purchase = ProductPurchase.objects.filter(
#                 product=product,
#                 purchase__bill_date__lt=start_date_obj
#             ).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")

#             opening_sale = Decimal("0.00")
#             for bill in Bill.objects.filter(transaction_date__lt=start_date_obj).prefetch_related("bill_items"):
#                 for item in bill.bill_items.filter(product=product):
#                     opening_sale += item.product_quantity

#             opening_consumed = Decimal("0.00")
#             logs_before = ProductionLog.objects.filter(production_date__lt=start_date_obj)
#             for log in logs_before:
#                 boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
#                 for bom in boms:
#                     opening_consumed += Decimal(bom.quantity) * log.quantity_produced

#             opening_qty = opening_purchase - opening_sale - opening_consumed
#             balance = opening_qty

#             ledger_rows = [{
#                 "date": str(start_date_obj) if start_date_obj else "",
#                 "miti": "",
#                 "particular": "Opening Stock (Fallback)",
#                 "type": "Opening",
#                 "txn_no": "",
#                 "in_qty": float(opening_purchase),
#                 "out_qty": float(opening_sale + opening_consumed),
#                 "balance_qty": float(balance)
#             }]

#         # -------------------- Purchases (one row per purchase) --------------------
#         purchases = ProductPurchase.objects.filter(product=product)
#         if start_date_obj:
#             purchases = purchases.filter(purchase__bill_date__gte=start_date_obj)
#         if end_date_obj:
#             purchases = purchases.filter(purchase__bill_date__lte=end_date_obj)

#         for pp in purchases.select_related("purchase"):
#             vendor_name = pp.purchase.vendor.name if pp.purchase.vendor else ""
#             entry = {
#                 "date": str(pp.purchase.bill_date),
#                 "miti": "",
#                 "particular": vendor_name,
#                 "type": "Purchase",
#                 "txn_no": pp.purchase.bill_no,
#                 "in_qty": float(pp.quantity),
#                 "out_qty": 0,
#             }
#             balance += Decimal(entry["in_qty"])
#             entry["balance_qty"] = float(balance)
#             ledger_rows.append(entry)

#         # -------------------- Sales (one row per bill item) --------------------
#         bills = Bill.objects.all()
#         if start_date_obj:
#             bills = bills.filter(transaction_date__gte=start_date_obj)
#         if end_date_obj:
#             bills = bills.filter(transaction_date__lte=end_date_obj)

#         bills = bills.prefetch_related("bill_items")

#         for bill in bills:
#             for item in bill.bill_items.filter(product=product):
#                 customer = bill.customer_name or "Cash Sales"
#                 entry = {
#                     "date": str(bill.transaction_date),
#                     "miti": bill.transaction_miti or "",
#                     "particular": customer,
#                     "type": "Sale",
#                     "txn_no": bill.invoice_number,
#                     "in_qty": 0,
#                     "out_qty": float(item.product_quantity),
#                 }
#                 balance -= Decimal(entry["out_qty"])
#                 entry["balance_qty"] = float(balance)
#                 ledger_rows.append(entry)

#         # -------------------- Consumptions (one row per component usage) --------------------
#         production_logs = ProductionLog.objects.all()
#         if start_date_obj:
#             production_logs = production_logs.filter(production_date__gte=start_date_obj)
#         if end_date_obj:
#             production_logs = production_logs.filter(production_date__lte=end_date_obj)

#         for log in production_logs:
#             boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
#             for bom in boms:
#                 consumed_qty = Decimal(bom.quantity) * log.quantity_produced
#                 entry = {
#                     "date": str(log.production_date),
#                     "miti": log.production_nepali_date or "",
#                     "particular": log.product.title,
#                     "type": "Consumed",
#                     "txn_no": f"STO-{log.id}",
#                     "in_qty": 0,
#                     "out_qty": float(consumed_qty),
#                 }
#                 balance -= Decimal(entry["out_qty"])
#                 entry["balance_qty"] = float(balance)
#                 ledger_rows.append(entry)

#         # -------------------- Final sort --------------------
#         ledger_rows_sorted = sorted(ledger_rows, key=lambda x: x["date"])
#         return Response(ledger_rows_sorted, status=200)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Sum
# from datetime import datetime
# from decimal import Decimal
# from bill.models import Bill
# from product.models import Product, ProductionLog, ProductOpeningStock, ProductBOM
# from purchase.models import ProductPurchase


# class RawMaterialsReportView(APIView):
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

#         # -------------------- Opening Stock --------------------
#         opening_entry = ProductOpeningStock.objects.filter(
#             product=product,
#             entry_date=start_date_obj
#         ).aggregate(total=Sum("opening_quantity"))["total"]

#         ledger_rows = []

#         if opening_entry is not None:
#             opening_qty = opening_entry
#             balance = opening_qty
#             ledger_rows.append({
#                 "date": str(start_date_obj),
#                 "miti": "",
#                 "particular": "Opening Stock",
#                 "type": "Opening",
#                 "txn_no": "",
#                 "in_qty": float(opening_qty),
#                 "out_qty": 0,
#                 "balance_qty": float(balance),
#                 "date_obj": start_date_obj
#             })
#         else:
#             opening_purchase = ProductPurchase.objects.filter(
#                 product=product,
#                 purchase__bill_date__lt=start_date_obj
#             ).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")

#             opening_sale = Decimal("0.00")
#             for bill in Bill.objects.filter(transaction_date__lt=start_date_obj).prefetch_related("bill_items"):
#                 for item in bill.bill_items.filter(product=product):
#                     opening_sale += item.product_quantity

#             opening_consumed = Decimal("0.00")
#             logs_before = ProductionLog.objects.filter(production_date__lt=start_date_obj)
#             for log in logs_before:
#                 boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
#                 for bom in boms:
#                     opening_consumed += Decimal(bom.quantity) * log.quantity_produced

#             opening_qty = opening_purchase - opening_sale - opening_consumed
#             balance = opening_qty

#             ledger_rows.append({
#                 "date": str(start_date_obj),
#                 "miti": "",
#                 "particular": "Opening Stock (Fallback)",
#                 "type": "Opening",
#                 "txn_no": "",
#                 "in_qty": float(opening_purchase),
#                 "out_qty": float(opening_sale + opening_consumed),
#                 "balance_qty": float(balance),
#                 "date_obj": start_date_obj
#             })

#         # -------------------- Collect all entries --------------------
#         all_entries = []

#         # Purchases
#         purchases = ProductPurchase.objects.filter(product=product)
#         if start_date_obj:
#             purchases = purchases.filter(purchase__bill_date__gte=start_date_obj)
#         if end_date_obj:
#             purchases = purchases.filter(purchase__bill_date__lte=end_date_obj)

#         for pp in purchases.select_related("purchase"):
#             vendor_name = pp.purchase.vendor.name if pp.purchase.vendor else ""
#             all_entries.append({
#                 "date": str(pp.purchase.bill_date),
#                 "date_obj": pp.purchase.bill_date,
#                 "miti": "",
#                 "particular": vendor_name,
#                 "type": "Purchase",
#                 "txn_no": pp.purchase.bill_no,
#                 "in_qty": float(pp.quantity),
#                 "out_qty": 0,
#             })

#         # Sales
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

#         # Consumption
#         production_logs = ProductionLog.objects.all()
#         if start_date_obj:
#             production_logs = production_logs.filter(production_date__gte=start_date_obj)
#         if end_date_obj:
#             production_logs = production_logs.filter(production_date__lte=end_date_obj)

#         for log in production_logs:
#             boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
#             for bom in boms:
#                 consumed_qty = Decimal(bom.quantity) * log.quantity_produced
#                 all_entries.append({
#                     "date": str(log.production_date),
#                     "date_obj": log.production_date,
#                     "miti": log.production_nepali_date or "",
#                     "particular": log.product.title,
#                     "type": "Consumed",
#                     "txn_no": f"STO-{log.id}",
#                     "in_qty": 0,
#                     "out_qty": float(consumed_qty),
#                 })

#         # -------------------- Sort all entries and update running balance --------------------
#         all_entries_sorted = sorted(all_entries, key=lambda x: x["date_obj"])
#         for entry in all_entries_sorted:
#             balance += Decimal(entry["in_qty"]) - Decimal(entry["out_qty"])
#             entry["balance_qty"] = float(balance)
#             ledger_rows.append(entry)

#         # -------------------- Clean and Return --------------------
#         for row in ledger_rows:
#             row.pop("date_obj", None)

#         return Response(ledger_rows, status=200)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from bill.models import Bill
from product.models import Product, ProductionLog, ProductOpeningStock, ProductBOM
from purchase.models import ProductPurchase
from purchase.models import ImportProductPurchase  # adjust path if needed


class RawMaterialsReportView(APIView):
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

        ledger_rows = []

        # -------------------- Opening Stock --------------------
        opening_entry = ProductOpeningStock.objects.filter(
            product=product,
            entry_date=start_date_obj
        ).aggregate(total=Sum("opening_quantity"))["total"]

        if opening_entry is not None:
            opening_qty = opening_entry
            balance = opening_qty
            ledger_rows.append({
                "date": str(start_date_obj),
                "miti": "",
                "particular": "Opening Stock",
                "type": "Opening",
                "txn_no": "",
                "in_qty": float(opening_qty),
                "out_qty": 0,
                "balance_qty": float(balance),
                "date_obj": start_date_obj
            })
        else:
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

            opening_consumed = Decimal("0.00")
            logs_before = ProductionLog.objects.filter(production_date__lt=start_date_obj)
            for log in logs_before:
                boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
                for bom in boms:
                    opening_consumed += Decimal(bom.quantity) * log.quantity_produced

            opening_qty = opening_purchase + opening_import - opening_sale - opening_consumed
            balance = opening_qty

            ledger_rows.append({
                "date": str(start_date_obj),
                "miti": "",
                "particular": "Opening Stock (Fallback)",
                "type": "Opening",
                "txn_no": "",
                "in_qty": float(opening_purchase + opening_import),
                "out_qty": float(opening_sale + opening_consumed),
                "balance_qty": float(balance),
                "date_obj": start_date_obj
            })

        # -------------------- Collect all entries --------------------
        all_entries = []

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

        # Sales
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

        # Consumption
        production_logs = ProductionLog.objects.all()
        if start_date_obj:
            production_logs = production_logs.filter(production_date__gte=start_date_obj)
        if end_date_obj:
            production_logs = production_logs.filter(production_date__lte=end_date_obj)

        for log in production_logs:
            boms = ProductBOM.objects.filter(parent_product=log.product, component_product=product)
            for bom in boms:
                consumed_qty = Decimal(bom.quantity) * log.quantity_produced
                all_entries.append({
                    "date": str(log.production_date),
                    "date_obj": log.production_date,
                    "miti": log.production_nepali_date or "",
                    "particular": log.product.title,
                    "type": "Consumed",
                    "txn_no": f"STO-{log.id}",
                    "in_qty": 0,
                    "out_qty": float(consumed_qty),
                })

        # -------------------- Sort all entries and calculate balance --------------------
        all_entries_sorted = sorted(all_entries, key=lambda x: x["date_obj"])
        for entry in all_entries_sorted:
            balance += Decimal(entry["in_qty"]) - Decimal(entry["out_qty"])
            entry["balance_qty"] = float(balance)
            ledger_rows.append(entry)

        # -------------------- Clean and Return --------------------
        for row in ledger_rows:
            row.pop("date_obj", None)

        return Response(ledger_rows, status=200)
