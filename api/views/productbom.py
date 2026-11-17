# views.py
from rest_framework import generics
from product.models import ProductBOM
from api.serializers.productbom import ProductBOMSerializer

class ProductBOMCreateView(generics.CreateAPIView):
    queryset = ProductBOM.objects.all()
    serializer_class = ProductBOMSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import Product, ProductBOM
from api.serializers.productbom import ProductBOMSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import Product, ProductBOM
from api.serializers.productbom import ProductBOMSerializer

class ProductBOMBulkCreateView(APIView):
    def post(self, request):
        """
        Handles both creation and updating of BOM entries.

        Sample JSON:
        {
            "parent_product": 5,
            "components": [
                {"component_product": 1, "quantity": 12},
                {"component_product": 2, "quantity": 5.5},
                {"component_product": 3, "quantity": 0.25}
            ]
        }
        """
        data = request.data
        parent_id = data.get("parent_product")
        components = data.get("components", [])

        try:
            parent_product = Product.objects.get(id=parent_id)
        except Product.DoesNotExist:
            return Response({"error": "Invalid parent product ID"}, status=status.HTTP_400_BAD_REQUEST)

        if not components:
            return Response({"error": "No component items provided."}, status=status.HTTP_400_BAD_REQUEST)

        result_boms = []

        for component in components:
            component_id = component.get("component_product")
            quantity = component.get("quantity")
            # cost = component.get("cost")

            # if not component_id or quantity is None or cost is None:
            if not component_id or quantity is None:
                return Response(
                    {"error": "Each component must include 'component_product' and 'quantity' and 'cost'."},
                    status=400
                )

            try:
                # Check if BOM entry already exists
                bom_entry = ProductBOM.objects.get(
                    parent_product_id=parent_id,
                    component_product_id=component_id
                )
                # Update quantity
                bom_entry.quantity = quantity
                # bom_entry.cost = cost
                bom_entry.save()
                result_boms.append(ProductBOMSerializer(bom_entry).data)
            except ProductBOM.DoesNotExist:
                # Create new entry
                serializer = ProductBOMSerializer(data={
                    "parent_product": parent_id,
                    "component_product": component_id,
                    "quantity": quantity,
                    # "cost": cost,
                })
                if serializer.is_valid():
                    serializer.save()
                    result_boms.append(serializer.data)
                else:
                    return Response(serializer.errors, status=400)

        return Response({
            "message": "BOM items created/updated successfully",
            "data": result_boms
        }, status=status.HTTP_200_OK)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from product.utils import calculate_cost


class ProductBOMReportView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        bom_items = product.bom_items.select_related('component_product')
        components = []

        for item in bom_items:
            component = item.component_product
            unit_price = Decimal(component.price)
            quantity = Decimal(item.quantity)
            total = unit_price * quantity

            components.append({
                "component": component.title,
                "quantity": float(quantity),
                "unit": component.unit,
                "unit_price": float(unit_price),
                "total_cost": float(total)
            })

        unit_cost = float(calculate_cost(product))

        return Response({
            "parent_product": product.title,
            "unit_cost": unit_cost,
            "components": components
        })


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from product.utils import calculate_cost
from decimal import Decimal


class AllProductBOMReportView(APIView):
    def get(self, request):
        products_with_bom = Product.objects.filter(bom_items__isnull=False).distinct()
        result = []

        for product in products_with_bom:
            bom_items = product.bom_items.select_related('component_product')
            components = []

            for item in bom_items:
                component = item.component_product
                if component.is_produced and component.bom_items.exists():
                    print("Their was product")
                    unit_price = calculate_cost(component)
                else:

                    unit_price = component.price
                unit_price = Decimal(unit_price)
                quantity = Decimal(item.quantity)
                total = unit_price * quantity

                components.append({
                    "id": item.id,  # Add BOM item ID here
                    "component": component.title,
                    "quantity": float(quantity),
                    "unit": component.unit,
                    "unit_price": float(unit_price),
                    "total_cost": float(total)
                })

            unit_cost = float(calculate_cost(product))

            result.append({
                "parent_product": product.title,
                "unit_cost": unit_cost,
                "parent_product_unit": product.unit,
                "components": components
            })

        return Response(result)


from product.models import ProductionLog
from api.serializers.productbom import ProductionLogSerializer

class CreateProductionLogView(APIView):
    def post(self, request):
        """
        Example JSON:
        {
            "product": 5,
            "quantity_produced": "20.50",
            "note": "Evening shift"
        }
        """
        serializer = ProductionLogSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            product = Product.objects.filter(id=product_id, is_produced=True).first()
            if not product:
                return Response({"error": "Product is not marked as 'is_produced'."}, status=400)

            serializer.save()
            return Response({"message": "Production log created successfully.", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    

# views/production_log_bulk_create.py (or wherever appropriate)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from api.serializers.productbom import ProductionLogSerializer  # adjust path if needed

class BulkCreateProductionLogView(APIView):
    def post(self, request):
        """
        Accepts multiple production logs in one request.

        Example:
        {
            "logs": [
                {
                    "product": 5,
                    "quantity_produced": "20.50",
                    "note": "Evening shift"
                },
                {
                    "product": 7,
                    "quantity_produced": "10.00",
                    "note": "Morning batch"
                }
            ]
        }
        """
        logs = request.data.get("logs", [])
        if not logs:
            return Response({"error": "No logs provided."}, status=400)

        created_logs = []
        errors = []

        for index, log_data in enumerate(logs):
            serializer = ProductionLogSerializer(data=log_data)
            if serializer.is_valid():
                product = serializer.validated_data['product']
                if not product.is_produced:
                    errors.append({
                        "index": index,
                        "error": f"Product '{product.title}' is not marked as 'is_produced'."
                    })
                    continue
                serializer.save()
                created_logs.append(serializer.data)
            else:
                errors.append({
                    "index": index,
                    "error": serializer.errors
                })

        response = {"created": created_logs}
        if errors:
            response["errors"] = errors

        return Response(response, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import ProductionLog, Product
from product.utils import resolve_bom_components  # your recursive logic
from decimal import Decimal

class ProductionLogReportView(APIView):
    def get(self, request, log_id):
        try:
            production_log = ProductionLog.objects.select_related('product').get(id=log_id)
        except ProductionLog.DoesNotExist:
            return Response({"error": "ProductionLog not found."}, status=404)

        total_quantity = production_log.quantity_produced
        resolved = resolve_bom_components(production_log.product, total_quantity)

        components_list = []
        for product, qty in resolved.items():
            price = product.price or Decimal("0.00")
            total_price = price * qty

            components_list.append({
                "product": product.title,
                "unit": product.unit,
                "quantity": str(qty),
                "price": str(price),
                "total_price": str(total_price.quantize(Decimal("0.01")))
            })

        return Response({
            "product": production_log.product.title,
            "quantity_produced": str(total_quantity),
            "production_date": production_log.production_date,
            "note": production_log.note,
            "components_used": components_list
        })

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from collections import defaultdict
# from decimal import Decimal
# from datetime import datetime
# from product.models import ProductionLog, Product
# from product.utils import resolve_bom_components, get_direct_bom_components

# class ProductionSummaryReportView(APIView):
#     def get(self, request):
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")
#         only_parents = request.GET.get("include_only_parent_products") == "true"

#         if not start_date or not end_date:
#             return Response({"error": "start_date and end_date are required."}, status=400)

#         try:
#             start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
#             end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         logs = ProductionLog.objects.select_related("product").filter(
#             production_date__range=(start_date_obj, end_date_obj)
#         )

#         product_logs = defaultdict(list)
#         for log in logs:
#             product_logs[log.product].append(log)

#         final_response = []

#         for product, logs in product_logs.items():
#             total_qty = sum(log.quantity_produced for log in logs)
#             per_product_components = defaultdict(Decimal)

#             for log in logs:
#                 if only_parents:
#                     resolved = get_direct_bom_components(product, log.quantity_produced)
#                 else:
#                     resolved = resolve_bom_components(product, log.quantity_produced)

#                 for comp, qty in resolved.items():
#                     per_product_components[comp] += qty

#             components_list = []
#             for comp, qty in per_product_components.items():
#                 price = comp.price or Decimal("0.00")
#                 total_price = price * qty

#                 components_list.append({
#                     "product": comp.title,
#                     "unit": comp.unit,
#                     "quantity": str(qty),
#                     "price": str(price),
#                     "total_price": str(total_price.quantize(Decimal("0.01")))
#                 })

#             final_response.append({
#                 "product": product.title,
#                 "unit": product.unit,
#                 "total_quantity_produced": str(total_qty),
#                 "components_used": components_list
#             })

#         return Response({
#             "start_date": str(start_date_obj),
#             "end_date": str(end_date_obj),
#             "include_only_parent_products": only_parents,
#             "report": final_response
#         }, status=200)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import datetime
from product.models import ProductionLog
from product.utils import resolve_bom_components, get_direct_bom_components

class ProductionSummaryReportView(APIView):
    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        only_parents = request.GET.get("include_only_parent_products") == "true"

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse dates directly for DateField filtering
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        logs = ProductionLog.objects.select_related("product").filter(
            production_date__range=(start_date_obj, end_date_obj)
        ).order_by("production_date")

        individual_logs = []

        for log in logs:
            if only_parents:
                resolved_components = get_direct_bom_components(log.product, log.quantity_produced)
            else:
                resolved_components = resolve_bom_components(log.product, log.quantity_produced)

            components_list = []
            total_cost = Decimal("0.00")

            for component, qty in resolved_components.items():
                price = component.price or Decimal("0.00")
                total_price = price * qty
                total_cost += total_price

                components_list.append({
                    "product": component.title,
                    "unit": component.unit,
                    "quantity": str(qty),
                    "price": str(price),
                    "total_price": str(total_price.quantize(Decimal("0.01")))
                })

            individual_logs.append({
                "id": log.id,
                "product": log.product.title,
                "unit": log.product.unit,
                "quantity_produced": str(log.quantity_produced),
                "production_date": log.production_date.strftime("%Y-%m-%d"),
                "production_nepali_date": log.production_nepali_date,
                "note": log.note,
                "total_cost": str(total_cost.quantize(Decimal("0.01"))),
                "components_used": components_list
            })

        return Response({
            "start_date": str(start_date_obj),
            "end_date": str(end_date_obj),
            "include_only_parent_products": only_parents,
            "production_logs": individual_logs
        }, status=status.HTTP_200_OK)

class ProductBOMDeleteView(APIView):
    def delete(self, request, pk):
        """
        Delete a BOM component by its ID (pk).
        URL: /api/delete-bom/<pk>/
        """
        try:
            bom_entry = ProductBOM.objects.get(id=pk)
            bom_entry.delete()
            return Response({"message": "BOM component deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProductBOM.DoesNotExist:
            return Response({"error": "BOM component not found."}, status=status.HTTP_404_NOT_FOUND)
            
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import ProductionLog

class DeleteProductionLogView(APIView):
    def delete(self, request, pk):
        try:
            log = ProductionLog.objects.get(pk=pk)
            log.delete()
            return Response({"message": "Production log deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProductionLog.DoesNotExist:
            return Response({"error": "Production log not found."}, status=status.HTTP_404_NOT_FOUND)
            
            
from rest_framework.response import Response
from rest_framework import status
import jwt
from user.models import User
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class VerifyToken(APIView):
    # permission_classes = [IsAuthenticated]


    def get(self, request):
        
        # Get token from query parameter instead of headers
        token = request.GET.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=int(payload['user_id']))

            # Return user details
            return Response({'valid': True})

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
from rest_framework.response import Response
from rest_framework import status
import jwt
from user.models import User
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class VerifyToken(APIView):
    # permission_classes = [IsAuthenticated]


    def get(self, request):
        
        # Get token from query parameter instead of headers
        token = request.GET.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=int(payload['user_id']))

            # Return user details
            return Response({'valid': True})

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from product.models import Product
from product.models import ProductOpeningStock  # Adjust path if needed
from django.db import IntegrityError

class ProductOpeningStockBulkCreateView(APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Expected a list of opening stock records."}, status=400)

        success_records = []
        errors = []

        for item in data:
            product_id = item.get("product_id")
            opening_quantity = item.get("opening_quantity")
            entry_date = item.get("entry_date")

            if not all([product_id, opening_quantity, entry_date]):
                errors.append({"error": "Missing fields", "data": item})
                continue

            try:
                product = Product.objects.get(id=product_id)
                obj, created = ProductOpeningStock.objects.update_or_create(
                    product=product,
                    entry_date=entry_date,
                    defaults={"opening_quantity": Decimal(opening_quantity)}
                )
                success_records.append({
                    "product_id": product.id,
                    "entry_date": entry_date,
                    "opening_quantity": str(obj.opening_quantity),
                    "status": "created" if created else "updated"
                })
            except Product.DoesNotExist:
                errors.append({"error": "Product not found", "product_id": product_id})
            except IntegrityError as e:
                errors.append({"error": str(e), "data": item})
            except Exception as e:
                errors.append({"error": str(e), "data": item})

        return Response({
            "success": success_records,
            "errors": errors
        }, status=200 if success_records else 400)
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from product.models import Product
from product.utils import calculate_cost

class ProducedProductsAndItsBom(APIView):
    def get(self, request):
        # Get all products that are marked as produced
        produced_products = Product.objects.filter(is_produced=True).distinct()
        result = []

        for product in produced_products:
            bom_items = product.bom_items.select_related('component_product').all()
            components = []

            for item in bom_items:
                component = item.component_product

                # Recursively calculate cost if component is a produced product with BOM
                if component.is_produced and component.bom_items.exists():
                    unit_price = calculate_cost(component)
                else:
                    unit_price = component.price

                unit_price = Decimal(unit_price)
                quantity = Decimal(item.quantity)
                total = unit_price * quantity

                components.append({
                    "id": item.id,
                    "component": component.title,
                    "quantity": float(quantity),
                    "unit": component.unit,
                    "unit_price": float(unit_price),
                    "total_cost": float(total)
                })

            # Calculate unit cost even if no BOM exists
            unit_cost = float(calculate_cost(product))

            result.append({
                "parent_product": product.title,
                "unit_cost": unit_cost,
                "components": components  # will be empty if no BOM
            })

        return Response(result)

