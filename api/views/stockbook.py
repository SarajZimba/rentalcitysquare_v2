# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Sum
# from datetime import datetime
# from decimal import Decimal
# from collections import defaultdict
# from bill.models import Bill
# from product.models import Product, ProductionLog, ProductOpeningStock, ProductBOM, ProductCategory
# from purchase.models import ProductPurchase, ImportProductPurchase

# class StockBookSummaryAPI(APIView):
#     def get(self, request):
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")

#         try:
#             start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
#             end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         titles = ["Raw Materials", "Work In Progress", "Finish Goods"]
#         product_categories = ProductCategory.objects.filter(title__in=titles)
#         categories = product_categories.prefetch_related("product_set").all()
#         all_boms = ProductBOM.objects.all()

#         bills_before = list(Bill.objects.filter(transaction_date__lt=start_date_obj, status=True).prefetch_related("bill_items"))
#         bills_in_range = list(Bill.objects.filter(transaction_date__gte=start_date_obj, transaction_date__lte=end_date_obj, status=True).prefetch_related("bill_items"))
#         bills_return = list(Bill.objects.filter(transaction_date__gte=start_date_obj, transaction_date__lte=end_date_obj, status=False).prefetch_related("bill_items"))

#         logs_before = list(ProductionLog.objects.filter(production_date__lt=start_date_obj))
#         logs_in_range = list(ProductionLog.objects.filter(production_date__gte=start_date_obj, production_date__lte=end_date_obj))

#         # Build lookup maps
#         bom_by_component = defaultdict(list)
#         for bom in all_boms:
#             bom_by_component[bom.component_product_id].append(bom)

#         bill_items_by_product = defaultdict(list)
#         for bill in bills_in_range:
#             for item in bill.bill_items.all():
#                 bill_items_by_product[item.product_id].append(item)

#         bill_items_before_by_product = defaultdict(list)
#         for bill in bills_before:
#             for item in bill.bill_items.all():
#                 bill_items_before_by_product[item.product_id].append(item)

#         bill_items_return_by_product = defaultdict(list)
#         for bill in bills_return:
#             for item in bill.bill_items.all():
#                 bill_items_return_by_product[item.product_id].append(item)

#         report_data = []

#         for category in categories:
#             category_totals = {
#                 "opening_quantity": Decimal("0.00"),
#                 "stock_in": Decimal("0.00"),
#                 "stock_out": Decimal("0.00"),
#                 "purchase_quantity": Decimal("0.00"),
#                 "sales_quantity": Decimal("0.00"),
#                 "purchase_return_quantity": Decimal("0.00"),
#                 "sales_return_quantity": Decimal("0.00"),
#                 "closing_quantity": Decimal("0.00"),
#             }

#             products_data = []
#             products = category.product_set.all()

#             for product in products:
#                 # Opening Stock
#                 opening = ProductOpeningStock.objects.filter(product=product, entry_date=start_date_obj).aggregate(total=Sum("opening_quantity"))['total']
#                 if opening is not None:
#                     opening_qty = opening
#                 else:
#                     opening_purchase = ProductPurchase.objects.filter(product=product, purchase__bill_date__lt=start_date_obj, purchase__status=True).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
#                     opening_import = ImportProductPurchase.objects.filter(product=product, purchase__bill_date__lt=start_date_obj).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
#                     opening_sale = sum(item.product_quantity for item in bill_items_before_by_product[product.id])

#                     opening_consumed = Decimal("0.00")
#                     for log in logs_before:
#                         for bom in bom_by_component.get(product.id, []):
#                             if bom.parent_product_id == log.product_id:
#                                 opening_consumed += Decimal(bom.quantity) * log.quantity_produced

#                     opening_qty = opening_purchase + opening_import - opening_sale - opening_consumed

#                 # Stock In (Produced)
#                 stock_in = ProductionLog.objects.filter(product=product, production_date__gte=start_date_obj, production_date__lte=end_date_obj).aggregate(total=Sum("quantity_produced"))['total'] or Decimal("0.00")

#                 # Stock Out (Consumed)
#                 stock_out = Decimal("0.00")
#                 for log in logs_in_range:
#                     for bom in bom_by_component.get(product.id, []):
#                         if bom.parent_product_id == log.product_id:
#                             stock_out += Decimal(bom.quantity) * log.quantity_produced

#                 # Purchases
#                 purchase_qty = ProductPurchase.objects.filter(product=product, purchase__bill_date__gte=start_date_obj, purchase__bill_date__lte=end_date_obj, purchase__status=True).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
#                 import_qty = ImportProductPurchase.objects.filter(product=product, purchase__bill_date__gte=start_date_obj, purchase__bill_date__lte=end_date_obj).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
#                 total_purchase_qty = purchase_qty + import_qty

#                 # Sales
#                 sales_qty = sum(item.product_quantity for item in bill_items_by_product[product.id])

#                 # Returns
#                 purchase_return = ProductPurchase.objects.filter(product=product, purchase__bill_date__gte=start_date_obj, purchase__bill_date__lte=end_date_obj, purchase__status=False).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
#                 sales_return = sum(item.product_quantity for item in bill_items_return_by_product[product.id])

#                 # Closing Quantity
#                 closing_qty = opening_qty + stock_in + total_purchase_qty + sales_return - stock_out - sales_qty - purchase_return

#                 products_data.append({
#                     "particular": product.title,
#                     "code": product.id,
#                     "unit": product.unit,
#                     "opening_quantity": round(float(opening_qty), 2),
#                     "stock_in": round(float(stock_in), 2),
#                     "stock_out": round(float(stock_out), 2),
#                     "purchase_quantity": round(float(total_purchase_qty), 2),
#                     "sales_quantity": round(float(sales_qty), 2),
#                     "purchase_return_quantity": round(float(purchase_return), 2),
#                     "sales_return_quantity": round(float(sales_return), 2),
#                     "closing_quantity": round(float(closing_qty), 2),
#                 })

#                 # Add to category totals
#                 category_totals["opening_quantity"] += opening_qty
#                 category_totals["stock_in"] += stock_in
#                 category_totals["stock_out"] += stock_out
#                 category_totals["purchase_quantity"] += total_purchase_qty
#                 category_totals["sales_quantity"] += sales_qty
#                 category_totals["purchase_return_quantity"] += purchase_return
#                 category_totals["sales_return_quantity"] += sales_return
#                 category_totals["closing_quantity"] += closing_qty

#             # Add category-level totals along with product list
#             category_block = {
#                 "category": category.title,
#                 "opening_quantity": round(float(category_totals["opening_quantity"]), 2),
#                 "stock_in": round(float(category_totals["stock_in"]), 2),
#                 "stock_out": round(float(category_totals["stock_out"]), 2),
#                 "purchase_quantity": round(float(category_totals["purchase_quantity"]), 2),
#                 "sales_quantity": round(float(category_totals["sales_quantity"]), 2),
#                 "purchase_return_quantity": round(float(category_totals["purchase_return_quantity"]), 2),
#                 "sales_return_quantity": round(float(category_totals["sales_return_quantity"]), 2),
#                 "closing_quantity": round(float(category_totals["closing_quantity"]), 2),
#                 "products": products_data
#             }

#             report_data.append(category_block)

#         return Response(report_data, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from bill.models import Bill
from product.models import Product, ProductionLog, ProductOpeningStock, ProductBOM
from purchase.models import ProductPurchase, ImportProductPurchase


class StockBookSummaryAPI(APIView):
    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Two fixed categories, driven by Product.is_produced rather than
        # ProductCategory — is_produced=True is a Finished Good (something
        # made via BOM/ProductionLog), is_produced=False is a Raw Material.
        category_definitions = [
            ("Finished Goods", True),
            ("Raw Materials", False),
        ]

        all_boms = ProductBOM.objects.all()

        bills_before = list(Bill.objects.filter(transaction_date__lt=start_date_obj, status=True).prefetch_related("bill_items"))
        bills_in_range = list(Bill.objects.filter(transaction_date__gte=start_date_obj, transaction_date__lte=end_date_obj, status=True).prefetch_related("bill_items"))
        bills_return = list(Bill.objects.filter(transaction_date__gte=start_date_obj, transaction_date__lte=end_date_obj, status=False).prefetch_related("bill_items"))

        logs_before = list(ProductionLog.objects.filter(production_date__lt=start_date_obj))
        logs_in_range = list(ProductionLog.objects.filter(production_date__gte=start_date_obj, production_date__lte=end_date_obj))

        # Build lookup maps
        bom_by_component = defaultdict(list)
        for bom in all_boms:
            bom_by_component[bom.component_product_id].append(bom)

        bill_items_by_product = defaultdict(list)
        for bill in bills_in_range:
            for item in bill.bill_items.all():
                bill_items_by_product[item.product_id].append(item)

        bill_items_before_by_product = defaultdict(list)
        for bill in bills_before:
            for item in bill.bill_items.all():
                bill_items_before_by_product[item.product_id].append(item)

        bill_items_return_by_product = defaultdict(list)
        for bill in bills_return:
            for item in bill.bill_items.all():
                bill_items_return_by_product[item.product_id].append(item)

        report_data = []

        for category_title, is_produced_flag in category_definitions:
            category_totals = {
                "opening_quantity": Decimal("0.00"),
                "stock_in": Decimal("0.00"),
                "stock_out": Decimal("0.00"),
                "purchase_quantity": Decimal("0.00"),
                "sales_quantity": Decimal("0.00"),
                "purchase_return_quantity": Decimal("0.00"),
                "sales_return_quantity": Decimal("0.00"),
                "closing_quantity": Decimal("0.00"),
            }

            products_data = []
            products = Product.objects.filter(is_produced=is_produced_flag)

            for product in products:
                # Opening Stock
                opening = ProductOpeningStock.objects.filter(product=product, entry_date=start_date_obj).aggregate(total=Sum("opening_quantity"))['total']
                if opening is not None:
                    opening_qty = opening
                else:
                    opening_purchase = ProductPurchase.objects.filter(product=product, purchase__bill_date__lt=start_date_obj, purchase__status=True).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
                    opening_import = ImportProductPurchase.objects.filter(product=product, purchase__bill_date__lt=start_date_obj).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
                    opening_sale = sum(item.product_quantity for item in bill_items_before_by_product[product.id])

                    opening_consumed = Decimal("0.00")
                    for log in logs_before:
                        for bom in bom_by_component.get(product.id, []):
                            if bom.parent_product_id == log.product_id:
                                opening_consumed += Decimal(bom.quantity) * log.quantity_produced

                    opening_qty = opening_purchase + opening_import - opening_sale - opening_consumed

                # Stock In (Produced)
                stock_in = ProductionLog.objects.filter(product=product, production_date__gte=start_date_obj, production_date__lte=end_date_obj).aggregate(total=Sum("quantity_produced"))['total'] or Decimal("0.00")

                # Stock Out (Consumed)
                stock_out = Decimal("0.00")
                for log in logs_in_range:
                    for bom in bom_by_component.get(product.id, []):
                        if bom.parent_product_id == log.product_id:
                            stock_out += Decimal(bom.quantity) * log.quantity_produced

                # Purchases
                purchase_qty = ProductPurchase.objects.filter(product=product, purchase__bill_date__gte=start_date_obj, purchase__bill_date__lte=end_date_obj, purchase__status=True).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
                import_qty = ImportProductPurchase.objects.filter(product=product, purchase__bill_date__gte=start_date_obj, purchase__bill_date__lte=end_date_obj).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
                total_purchase_qty = purchase_qty + import_qty

                # Sales
                sales_qty = sum(item.product_quantity for item in bill_items_by_product[product.id])

                # Returns
                purchase_return = ProductPurchase.objects.filter(product=product, purchase__bill_date__gte=start_date_obj, purchase__bill_date__lte=end_date_obj, purchase__status=False).aggregate(total=Sum("quantity"))['total'] or Decimal("0.00")
                sales_return = sum(item.product_quantity for item in bill_items_return_by_product[product.id])

                # Closing Quantity
                closing_qty = opening_qty + stock_in + total_purchase_qty + sales_return - stock_out - sales_qty - purchase_return

                products_data.append({
                    "particular": product.title,
                    "code": product.id,
                    "unit": product.unit,
                    "opening_quantity": round(float(opening_qty), 2),
                    "stock_in": round(float(stock_in), 2),
                    "stock_out": round(float(stock_out), 2),
                    "purchase_quantity": round(float(total_purchase_qty), 2),
                    "sales_quantity": round(float(sales_qty), 2),
                    "purchase_return_quantity": round(float(purchase_return), 2),
                    "sales_return_quantity": round(float(sales_return), 2),
                    "closing_quantity": round(float(closing_qty), 2),
                })

                # Add to category totals
                category_totals["opening_quantity"] += opening_qty
                category_totals["stock_in"] += stock_in
                category_totals["stock_out"] += stock_out
                category_totals["purchase_quantity"] += total_purchase_qty
                category_totals["sales_quantity"] += sales_qty
                category_totals["purchase_return_quantity"] += purchase_return
                category_totals["sales_return_quantity"] += sales_return
                category_totals["closing_quantity"] += closing_qty

            # Add category-level totals along with product list
            category_block = {
                "category": category_title,
                "opening_quantity": round(float(category_totals["opening_quantity"]), 2),
                "stock_in": round(float(category_totals["stock_in"]), 2),
                "stock_out": round(float(category_totals["stock_out"]), 2),
                "purchase_quantity": round(float(category_totals["purchase_quantity"]), 2),
                "sales_quantity": round(float(category_totals["sales_quantity"]), 2),
                "purchase_return_quantity": round(float(category_totals["purchase_return_quantity"]), 2),
                "sales_return_quantity": round(float(category_totals["sales_return_quantity"]), 2),
                "closing_quantity": round(float(category_totals["closing_quantity"]), 2),
                "products": products_data
            }

            report_data.append(category_block)

        return Response(report_data, status=200)