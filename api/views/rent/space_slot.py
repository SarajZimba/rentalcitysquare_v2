# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from django.shortcuts import get_object_or_404
# from rent.models import SpaceSlot
# from api.serializers.rent.space_slot import SpaceSlotSerializer

# class SpaceSlotListCreateView(APIView):
#     """
#     List all spaces or create a new space
#     """
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         # Get all spaces
#         spaces = SpaceSlot.objects.all()
        
#         # Apply filters if provided
#         floor = request.query_params.get('floor')
#         status_filter = request.query_params.get('status')
        
#         if floor:
#             spaces = spaces.filter(floor=floor)
#         if status_filter:
#             spaces = spaces.filter(status=status_filter)
        
#         serializer = SpaceSlotSerializer(spaces, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = SpaceSlotSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class SpaceSlotDetailView(APIView):
#     """
#     Retrieve, update or delete a specific space
#     """
#     permission_classes = [AllowAny]
    
#     def get(self, request, pk):
#         space = get_object_or_404(SpaceSlot, pk=pk)
#         serializer = SpaceSlotSerializer(space)
#         return Response(serializer.data)
    
#     def put(self, request, pk):
#         space = get_object_or_404(SpaceSlot, pk=pk)
#         serializer = SpaceSlotSerializer(space, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def patch(self, request, pk):
#         space = get_object_or_404(SpaceSlot, pk=pk)
#         serializer = SpaceSlotSerializer(space, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request, pk):
#         space = get_object_or_404(SpaceSlot, pk=pk)
#         space.delete()
#         return Response({"message": "Space deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# class SpaceSlotAvailableView(APIView):
#     """
#     Get all available (vacant) spaces
#     """
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         vacant_spaces = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.VACANT)
#         serializer = SpaceSlotSerializer(vacant_spaces, many=True)
#         return Response(serializer.data)


# class SpaceSlotOccupiedView(APIView):
#     """
#     Get all occupied spaces
#     """
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         occupied_spaces = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.OCCUPIED)
#         serializer = SpaceSlotSerializer(occupied_spaces, many=True)
#         return Response(serializer.data)


# class SpaceSlotOccupyView(APIView):
#     """
#     Mark a space as occupied
#     """
#     permission_classes = [AllowAny]
    
#     def post(self, request, pk):
#         space = get_object_or_404(SpaceSlot, pk=pk)
        
#         if space.status == SpaceSlot.StatusChoices.OCCUPIED:
#             return Response(
#                 {"error": "This space is already occupied"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         space.occupy()
#         serializer = SpaceSlotSerializer(space)
#         return Response(serializer.data)


# class SpaceSlotVacateView(APIView):
#     """
#     Mark a space as vacant
#     """
#     permission_classes = [AllowAny]
    
#     def post(self, request, pk):
#         space = get_object_or_404(SpaceSlot, pk=pk)
        
#         if space.status == SpaceSlot.StatusChoices.VACANT:
#             return Response(
#                 {"error": "This space is already vacant"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         space.vacate()
#         serializer = SpaceSlotSerializer(space)
#         return Response(serializer.data)


# class SpaceSlotBulkCreateView(APIView):
#     """
#     Create multiple spaces at once
#     """
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         serializer = SpaceSlotSerializer(data=request.data, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class SpaceSlotStatsView(APIView):
#     """
#     Get statistics about spaces
#     """
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         total = SpaceSlot.objects.count()
#         vacant = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.VACANT).count()
#         occupied = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.OCCUPIED).count()
#         reserved = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.RESERVED).count()
#         maintenance = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.MAINTENANCE).count()
        
#         return Response({
#             'total': total,
#             'vacant': vacant,
#             'occupied': occupied,
#             'reserved': reserved,
#             'maintenance': maintenance,
#             'occupancy_rate': f"{(occupied / total * 100):.2f}%" if total > 0 else "0%"
#         })


# # import openpyxl
# # from decimal import Decimal, InvalidOperation
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from rest_framework.permissions import IsAuthenticated
# # from rent.models import SpaceSlot
# # from api.serializers.rent.space_slot import SpaceSlotSerializer, SpaceSlotBulkUploadSerializer


# # HEADER_MAP = {
# #     "floor": "floor",
# #     "space no": "spaceno",
# #     "space number": "spaceno",
# #     "spaceno": "spaceno",
# #     "status": "status",
# #     "initial nea reading": "initial_nea_reading",
# #     "nea reading": "initial_nea_reading",
# #     "initial diesel reading": "initial_diesel_reading",
# #     "diesel reading": "initial_diesel_reading",
# # }

# # VALID_STATUSES = {choice.lower(): choice for choice, _ in SpaceSlot.StatusChoices.choices}


# # def _parse_decimal(value):
# #     if value in (None, ""):
# #         return None
# #     try:
# #         return Decimal(str(value).strip())
# #     except (InvalidOperation, ValueError):
# #         return None


# # class SpaceSlotExcelBulkCreateView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         upload_serializer = SpaceSlotBulkUploadSerializer(data=request.data)
# #         upload_serializer.is_valid(raise_exception=True)
# #         excel_file = upload_serializer.validated_data['file']

# #         try:
# #             wb = openpyxl.load_workbook(excel_file, data_only=True)
# #         except Exception as e:
# #             return Response(
# #                 {"detail": f"Could not read Excel file: {e}"},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         sheet = wb.active
# #         rows = list(sheet.iter_rows(values_only=True))

# #         if not rows:
# #             return Response({"detail": "The sheet is empty."}, status=status.HTTP_400_BAD_REQUEST)

# #         # Find header row: first row containing "floor"
# #         header_row_idx = None
# #         col_index_map = {}
# #         for i, row in enumerate(rows):
# #             normalized = [str(c).strip().lower() if c is not None else "" for c in row]
# #             if "floor" in normalized:
# #                 header_row_idx = i
# #                 for col_idx, header_text in enumerate(normalized):
# #                     field = HEADER_MAP.get(header_text)
# #                     if field:
# #                         col_index_map[field] = col_idx
# #                 break

# #         if header_row_idx is None:
# #             return Response(
# #                 {"detail": "Could not find a 'Floor' header row in the sheet."},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         if "floor" not in col_index_map:
# #             return Response(
# #                 {"detail": "Floor column is required."},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         created, skipped, errors = [], [], []

# #         for row_num, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
# #             def get(field):
# #                 idx = col_index_map.get(field)
# #                 if idx is None or idx >= len(row):
# #                     return None
# #                 val = row[idx]
# #                 return str(val).strip() if val is not None else None

# #             floor = get("floor")
# #             if not floor:
# #                 continue  # blank row, skip

# #             spaceno = get("spaceno")

# #             raw_status = get("status")
# #             resolved_status = VALID_STATUSES.get(raw_status.lower()) if raw_status else SpaceSlot.StatusChoices.VACANT
# #             if raw_status and resolved_status is None:
# #                 errors.append({
# #                     "row": row_num,
# #                     "floor": floor,
# #                     "spaceno": spaceno,
# #                     "errors": {"status": f"Invalid status '{raw_status}'. Must be one of {list(VALID_STATUSES.values())}."}
# #                 })
# #                 continue

# #             nea_raw = get("initial_nea_reading")
# #             diesel_raw = get("initial_diesel_reading")
# #             nea = _parse_decimal(nea_raw) if nea_raw is not None else Decimal("0")
# #             diesel = _parse_decimal(diesel_raw) if diesel_raw is not None else Decimal("0")

# #             if nea_raw and nea is None:
# #                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
# #                                 "errors": {"initial_nea_reading": f"Invalid number '{nea_raw}'."}})
# #                 continue
# #             if diesel_raw and diesel is None:
# #                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
# #                                 "errors": {"initial_diesel_reading": f"Invalid number '{diesel_raw}'."}})
# #                 continue

# #             data = {
# #                 "floor": floor,
# #                 "spaceno": spaceno,
# #                 "status": resolved_status,
# #                 "initial_nea_reading": nea,
# #                 "initial_diesel_reading": diesel,
# #             }

# #             serializer = SpaceSlotSerializer(data=data)
# #             if serializer.is_valid():
# #                 if spaceno:
# #                     obj, was_created = SpaceSlot.objects.update_or_create(
# #                         floor=floor, spaceno=spaceno, defaults=data
# #                     )
# #                     (created if was_created else skipped).append(f"{floor} - {spaceno}")
# #                 else:
# #                     obj = SpaceSlot.objects.create(**data)
# #                     created.append(f"{floor} - (no space no)")
# #             else:
# #                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno, "errors": serializer.errors})

# #         return Response(
# #             {
# #                 "created_count": len(created),
# #                 "updated_count": len(skipped),
# #                 "created": created,
# #                 "updated": skipped,
# #                 "errors": errors,
# #             },
# #             status=status.HTTP_200_OK,
# #         )

# import openpyxl
# from decimal import Decimal, InvalidOperation
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rent.models import SpaceSlot
# from api.serializers.rent.space_slot import SpaceSlotSerializer, SpaceSlotBulkUploadSerializer


# # Fixed column positions (0-indexed), based on: S.N | Spaceno | Initial Nea Reading | Initial Diesel Reading | Floor
# COL_SPACENO = 1
# COL_NEA_READING = 2
# COL_DIESEL_READING = 3
# COL_FLOOR = 4

# HEADER_ROWS_TO_SKIP = 1  # one header row at the top


# def _parse_decimal(value):
#     if value in (None, ""):
#         return None
#     try:
#         return Decimal(str(value).strip())
#     except (InvalidOperation, ValueError):
#         return None


# class SpaceSlotExcelBulkCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         upload_serializer = SpaceSlotBulkUploadSerializer(data=request.data)
#         upload_serializer.is_valid(raise_exception=True)
#         excel_file = upload_serializer.validated_data['file']

#         try:
#             wb = openpyxl.load_workbook(excel_file, data_only=True)
#         except Exception as e:
#             return Response(
#                 {"detail": f"Could not read Excel file: {e}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         sheet = wb.active
#         rows = list(sheet.iter_rows(values_only=True))

#         if not rows:
#             return Response({"detail": "The sheet is empty."}, status=status.HTTP_400_BAD_REQUEST)

#         data_rows = rows[HEADER_ROWS_TO_SKIP:]

#         def get(row, idx):
#             if idx >= len(row) or row[idx] is None:
#                 return None
#             val = str(row[idx]).strip()
#             return val if val != "" else None

#         created, skipped, errors = [], [], []

#         for row_num, row in enumerate(data_rows, start=HEADER_ROWS_TO_SKIP + 1):
#             floor = get(row, COL_FLOOR)
#             spaceno = get(row, COL_SPACENO)

#             if not floor and not spaceno:
#                 continue  # fully blank row, skip

#             if not floor:
#                 errors.append({"row": row_num, "spaceno": spaceno, "errors": {"floor": "Floor is required."}})
#                 continue

#             nea_raw = get(row, COL_NEA_READING)
#             diesel_raw = get(row, COL_DIESEL_READING)
#             nea = _parse_decimal(nea_raw) if nea_raw is not None else Decimal("0")
#             diesel = _parse_decimal(diesel_raw) if diesel_raw is not None else Decimal("0")

#             if nea_raw and nea is None:
#                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
#                                 "errors": {"initial_nea_reading": f"Invalid number '{nea_raw}'."}})
#                 continue
#             if diesel_raw and diesel is None:
#                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
#                                 "errors": {"initial_diesel_reading": f"Invalid number '{diesel_raw}'."}})
#                 continue

#             data = {
#                 "floor": floor,
#                 "spaceno": spaceno,
#                 "status": SpaceSlot.StatusChoices.VACANT,
#                 "initial_nea_reading": nea,
#                 "initial_diesel_reading": diesel,
#             }

#             serializer = SpaceSlotSerializer(data=data)
#             if serializer.is_valid():
#                 if spaceno:
#                     obj, was_created = SpaceSlot.objects.update_or_create(
#                         floor=floor, spaceno=spaceno, defaults=data
#                     )
#                     (created if was_created else skipped).append(f"{floor} - {spaceno}")
#                 else:
#                     obj = SpaceSlot.objects.create(**data)
#                     created.append(f"{floor} - (no space no)")
#             else:
#                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno, "errors": serializer.errors})

#         return Response(
#             {
#                 "created_count": len(created),
#                 "updated_count": len(skipped),
#                 "created": created,
#                 "updated": skipped,
#                 "errors": errors,
#             },
#             status=status.HTTP_200_OK,
#         )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rent.models import SpaceSlot
from api.serializers.rent.space_slot import SpaceSlotSerializer

# class SpaceSlotListCreateView(APIView):
#     """
#     List all spaces or create a new space
#     """
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         # Get all spaces
#         spaces = SpaceSlot.objects.all()
        
#         # Apply filters if provided
#         floor = request.query_params.get('floor')
#         status_filter = request.query_params.get('status')
        
#         if floor:
#             spaces = spaces.filter(floor=floor)
#         if status_filter:
#             spaces = spaces.filter(status=status_filter)
        
#         serializer = SpaceSlotSerializer(spaces, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = SpaceSlotSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.db.models import Prefetch
from rent.models import BillRent

class SpaceSlotListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        latest_bill_rent_qs = BillRent.objects.filter(is_deleted=False).order_by('-bill_month')

        spaces = SpaceSlot.objects.prefetch_related(
            Prefetch(
                'bill_rent_items',
                queryset=latest_bill_rent_qs,
                to_attr='latest_bill_rent_list',
            )
        )

        floor = request.query_params.get('floor')
        status_filter = request.query_params.get('status')

        if floor:
            spaces = spaces.filter(floor=floor)
        if status_filter:
            spaces = spaces.filter(status=status_filter)

        serializer = SpaceSlotSerializer(spaces, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SpaceSlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class SpaceSlotDetailView(APIView):
    """
    Retrieve, update or delete a specific space
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        space = get_object_or_404(SpaceSlot, pk=pk)
        serializer = SpaceSlotSerializer(space)
        return Response(serializer.data)
    
    def put(self, request, pk):
        space = get_object_or_404(SpaceSlot, pk=pk)
        serializer = SpaceSlotSerializer(space, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        space = get_object_or_404(SpaceSlot, pk=pk)
        serializer = SpaceSlotSerializer(space, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        space = get_object_or_404(SpaceSlot, pk=pk)
        space.delete()
        return Response({"message": "Space deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SpaceSlotAvailableView(APIView):
    """
    Get all available (vacant) spaces
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        vacant_spaces = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.VACANT)
        serializer = SpaceSlotSerializer(vacant_spaces, many=True)
        return Response(serializer.data)


class SpaceSlotOccupiedView(APIView):
    """
    Get all occupied spaces
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        occupied_spaces = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.OCCUPIED)
        serializer = SpaceSlotSerializer(occupied_spaces, many=True)
        return Response(serializer.data)


class SpaceSlotOccupyView(APIView):
    """
    Mark a space as occupied
    """
    permission_classes = [AllowAny]
    
    def post(self, request, pk):
        space = get_object_or_404(SpaceSlot, pk=pk)
        
        if space.status == SpaceSlot.StatusChoices.OCCUPIED:
            return Response(
                {"error": "This space is already occupied"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        space.occupy()
        serializer = SpaceSlotSerializer(space)
        return Response(serializer.data)


class SpaceSlotVacateView(APIView):
    """
    Mark a space as vacant
    """
    permission_classes = [AllowAny]
    
    def post(self, request, pk):
        space = get_object_or_404(SpaceSlot, pk=pk)
        
        if space.status == SpaceSlot.StatusChoices.VACANT:
            return Response(
                {"error": "This space is already vacant"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        space.vacate()
        serializer = SpaceSlotSerializer(space)
        return Response(serializer.data)


class SpaceSlotBulkCreateView(APIView):
    """
    Create multiple spaces at once
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SpaceSlotSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpaceSlotStatsView(APIView):
    """
    Get statistics about spaces
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        total = SpaceSlot.objects.count()
        vacant = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.VACANT).count()
        occupied = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.OCCUPIED).count()
        reserved = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.RESERVED).count()
        maintenance = SpaceSlot.objects.filter(status=SpaceSlot.StatusChoices.MAINTENANCE).count()
        
        return Response({
            'total': total,
            'vacant': vacant,
            'occupied': occupied,
            'reserved': reserved,
            'maintenance': maintenance,
            'occupancy_rate': f"{(occupied / total * 100):.2f}%" if total > 0 else "0%"
        })


# import openpyxl
# from decimal import Decimal, InvalidOperation
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rent.models import SpaceSlot
# from api.serializers.rent.space_slot import SpaceSlotSerializer, SpaceSlotBulkUploadSerializer


# HEADER_MAP = {
#     "floor": "floor",
#     "space no": "spaceno",
#     "space number": "spaceno",
#     "spaceno": "spaceno",
#     "status": "status",
#     "initial nea reading": "initial_nea_reading",
#     "nea reading": "initial_nea_reading",
#     "initial diesel reading": "initial_diesel_reading",
#     "diesel reading": "initial_diesel_reading",
# }

# VALID_STATUSES = {choice.lower(): choice for choice, _ in SpaceSlot.StatusChoices.choices}


# def _parse_decimal(value):
#     if value in (None, ""):
#         return None
#     try:
#         return Decimal(str(value).strip())
#     except (InvalidOperation, ValueError):
#         return None


# class SpaceSlotExcelBulkCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         upload_serializer = SpaceSlotBulkUploadSerializer(data=request.data)
#         upload_serializer.is_valid(raise_exception=True)
#         excel_file = upload_serializer.validated_data['file']

#         try:
#             wb = openpyxl.load_workbook(excel_file, data_only=True)
#         except Exception as e:
#             return Response(
#                 {"detail": f"Could not read Excel file: {e}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         sheet = wb.active
#         rows = list(sheet.iter_rows(values_only=True))

#         if not rows:
#             return Response({"detail": "The sheet is empty."}, status=status.HTTP_400_BAD_REQUEST)

#         # Find header row: first row containing "floor"
#         header_row_idx = None
#         col_index_map = {}
#         for i, row in enumerate(rows):
#             normalized = [str(c).strip().lower() if c is not None else "" for c in row]
#             if "floor" in normalized:
#                 header_row_idx = i
#                 for col_idx, header_text in enumerate(normalized):
#                     field = HEADER_MAP.get(header_text)
#                     if field:
#                         col_index_map[field] = col_idx
#                 break

#         if header_row_idx is None:
#             return Response(
#                 {"detail": "Could not find a 'Floor' header row in the sheet."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if "floor" not in col_index_map:
#             return Response(
#                 {"detail": "Floor column is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         created, skipped, errors = [], [], []

#         for row_num, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
#             def get(field):
#                 idx = col_index_map.get(field)
#                 if idx is None or idx >= len(row):
#                     return None
#                 val = row[idx]
#                 return str(val).strip() if val is not None else None

#             floor = get("floor")
#             if not floor:
#                 continue  # blank row, skip

#             spaceno = get("spaceno")

#             raw_status = get("status")
#             resolved_status = VALID_STATUSES.get(raw_status.lower()) if raw_status else SpaceSlot.StatusChoices.VACANT
#             if raw_status and resolved_status is None:
#                 errors.append({
#                     "row": row_num,
#                     "floor": floor,
#                     "spaceno": spaceno,
#                     "errors": {"status": f"Invalid status '{raw_status}'. Must be one of {list(VALID_STATUSES.values())}."}
#                 })
#                 continue

#             nea_raw = get("initial_nea_reading")
#             diesel_raw = get("initial_diesel_reading")
#             nea = _parse_decimal(nea_raw) if nea_raw is not None else Decimal("0")
#             diesel = _parse_decimal(diesel_raw) if diesel_raw is not None else Decimal("0")

#             if nea_raw and nea is None:
#                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
#                                 "errors": {"initial_nea_reading": f"Invalid number '{nea_raw}'."}})
#                 continue
#             if diesel_raw and diesel is None:
#                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
#                                 "errors": {"initial_diesel_reading": f"Invalid number '{diesel_raw}'."}})
#                 continue

#             data = {
#                 "floor": floor,
#                 "spaceno": spaceno,
#                 "status": resolved_status,
#                 "initial_nea_reading": nea,
#                 "initial_diesel_reading": diesel,
#             }

#             serializer = SpaceSlotSerializer(data=data)
#             if serializer.is_valid():
#                 if spaceno:
#                     obj, was_created = SpaceSlot.objects.update_or_create(
#                         floor=floor, spaceno=spaceno, defaults=data
#                     )
#                     (created if was_created else skipped).append(f"{floor} - {spaceno}")
#                 else:
#                     obj = SpaceSlot.objects.create(**data)
#                     created.append(f"{floor} - (no space no)")
#             else:
#                 errors.append({"row": row_num, "floor": floor, "spaceno": spaceno, "errors": serializer.errors})

#         return Response(
#             {
#                 "created_count": len(created),
#                 "updated_count": len(skipped),
#                 "created": created,
#                 "updated": skipped,
#                 "errors": errors,
#             },
#             status=status.HTTP_200_OK,
#         )

import openpyxl
from decimal import Decimal, InvalidOperation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rent.models import SpaceSlot
from api.serializers.rent.space_slot import SpaceSlotSerializer, SpaceSlotBulkUploadSerializer


# Fixed column positions (0-indexed), based on: S.N | Spaceno | Initial Nea Reading | Initial Diesel Reading | Floor
COL_SPACENO = 1
COL_NEA_READING = 2
COL_DIESEL_READING = 3
COL_FLOOR = 4

HEADER_ROWS_TO_SKIP = 1  # one header row at the top


def _parse_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


class SpaceSlotExcelBulkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        upload_serializer = SpaceSlotBulkUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        excel_file = upload_serializer.validated_data['file']

        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
        except Exception as e:
            return Response(
                {"detail": f"Could not read Excel file: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))

        if not rows:
            return Response({"detail": "The sheet is empty."}, status=status.HTTP_400_BAD_REQUEST)

        data_rows = rows[HEADER_ROWS_TO_SKIP:]

        def get(row, idx):
            if idx >= len(row) or row[idx] is None:
                return None
            val = str(row[idx]).strip()
            return val if val != "" else None

        created, skipped, errors = [], [], []

        for row_num, row in enumerate(data_rows, start=HEADER_ROWS_TO_SKIP + 1):
            floor = get(row, COL_FLOOR)
            spaceno = get(row, COL_SPACENO)

            if not floor and not spaceno:
                continue  # fully blank row, skip

            if not floor:
                errors.append({"row": row_num, "spaceno": spaceno, "errors": {"floor": "Floor is required."}})
                continue

            nea_raw = get(row, COL_NEA_READING)
            diesel_raw = get(row, COL_DIESEL_READING)
            nea = _parse_decimal(nea_raw) if nea_raw is not None else Decimal("0")
            diesel = _parse_decimal(diesel_raw) if diesel_raw is not None else Decimal("0")

            if nea_raw and nea is None:
                errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
                                "errors": {"initial_nea_reading": f"Invalid number '{nea_raw}'."}})
                continue
            if diesel_raw and diesel is None:
                errors.append({"row": row_num, "floor": floor, "spaceno": spaceno,
                                "errors": {"initial_diesel_reading": f"Invalid number '{diesel_raw}'."}})
                continue

            data = {
                "floor": floor,
                "spaceno": spaceno,
                "status": SpaceSlot.StatusChoices.VACANT,
                "initial_nea_reading": nea,
                "initial_diesel_reading": diesel,
            }

            serializer = SpaceSlotSerializer(data=data)
            if serializer.is_valid():
                if spaceno:
                    obj, was_created = SpaceSlot.objects.update_or_create(
                        floor=floor, spaceno=spaceno, defaults=data
                    )
                    (created if was_created else skipped).append(f"{floor} - {spaceno}")
                else:
                    obj = SpaceSlot.objects.create(**data)
                    created.append(f"{floor} - (no space no)")
            else:
                errors.append({"row": row_num, "floor": floor, "spaceno": spaceno, "errors": serializer.errors})

        return Response(
            {
                "created_count": len(created),
                "updated_count": len(skipped),
                "created": created,
                "updated": skipped,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )