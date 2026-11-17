# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rent.models import Business
from api.serializers.rent.business_using_slot import BusinessSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]  # remove/adjust as needed
    pagination_class = None


# import openpyxl
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rent.models import Business
# from api.serializers.rent.business_using_slot import BusinessSerializer, BusinessBulkUploadSerializer

# HEADER_MAP = {
#     "company name": "company_name",
#     "pan number": "pan_number",
#     "contact person": "contact_person",
#     "phone number": "contact_phone",
#     "contact phone": "contact_phone",
#     "email": "contact_email",
#     "contact email": "contact_email",
# }


# class BusinessExcelUploadView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         upload_serializer = BusinessBulkUploadSerializer(data=request.data)
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

#         header_row_idx = None
#         col_index_map = {}
#         for i, row in enumerate(rows):
#             normalized = [str(c).strip().lower() if c is not None else "" for c in row]
#             if "company name" in normalized:
#                 header_row_idx = i
#                 for col_idx, header_text in enumerate(normalized):
#                     field = HEADER_MAP.get(header_text)
#                     if field:
#                         col_index_map[field] = col_idx
#                 break

#         if header_row_idx is None:
#             return Response(
#                 {"detail": "Could not find a 'Company Name' header row in the sheet."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if "company_name" not in col_index_map:
#             return Response(
#                 {"detail": "Company Name column is required."},
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

#             company_name = get("company_name")
#             if not company_name:
#                 continue

#             data = {
#                 "company_name": company_name,
#                 "pan_number": (get("pan_number") or ""),
#                 "contact_person": get("contact_person"),
#                 "contact_phone": get("contact_phone"),
#                 "contact_email": get("contact_email"),
#             }

#             serializer = BusinessSerializer(data=data)
#             if serializer.is_valid():
#                 lookup = {"pan_number": data["pan_number"]} if data["pan_number"] else {"company_name": company_name}
#                 obj, was_created = Business.objects.update_or_create(**lookup, defaults=data)
#                 (created if was_created else skipped).append(obj.company_name)
#             else:
#                 errors.append({"row": row_num, "company_name": company_name, "errors": serializer.errors})

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
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rent.models import Business
from api.serializers.rent.business_using_slot import BusinessSerializer, BusinessBulkUploadSerializer

HEADER_MAP = {
    "company name": "company_name",
    "pan number": "pan_number",
    "contact person": "contact_person",
    "phone number": "contact_phone",
    "contact phone": "contact_phone",
    "email": "contact_email",
    "contact email": "contact_email",
}

# from user.models import Customer
# class BusinessExcelUploadView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         upload_serializer = BusinessBulkUploadSerializer(data=request.data)
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

#         header_row_idx = None
#         col_index_map = {}
#         for i, row in enumerate(rows):
#             normalized = [str(c).strip().lower() if c is not None else "" for c in row]
#             if "company name" in normalized:
#                 header_row_idx = i
#                 for col_idx, header_text in enumerate(normalized):
#                     field = HEADER_MAP.get(header_text)
#                     if field:
#                         col_index_map[field] = col_idx
#                 break

#         if header_row_idx is None:
#             return Response(
#                 {"detail": "Could not find a 'Company Name' header row in the sheet."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if "company_name" not in col_index_map:
#             return Response(
#                 {"detail": "Company Name column is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         created, errors = [], []


#         for row_num, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
#             def get(field):
#                 idx = col_index_map.get(field)
#                 if idx is None or idx >= len(row):
#                     return None
#                 val = row[idx]
#                 return str(val).strip() if val is not None else None

#             company_name = get("company_name")
#             if not company_name:
#                 continue

#             data = {
#                 "company_name": company_name,
#                 "pan_number": (get("pan_number") or ""),
#                 "contact_person": get("contact_person"),
#                 "contact_phone": get("contact_phone"),
#                 "contact_email": get("contact_email"),
#             }

#             serializer = BusinessSerializer(data=data)
#             if serializer.is_valid():
#                 customer = Customer.objects.create(
#                     name=company_name,
#                     tax_number=data["pan_number"] or None,
#                     contact_number=data["contact_phone"],
#                     email=data["contact_email"],
#                     created_by=request.user
#                 )
#                 obj = Business.objects.create(**data, customer=customer)
#                 created.append(obj.company_name)
#             else:
#                 errors.append({"row": row_num, "company_name": company_name, "errors": serializer.errors})

        # for row_num, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
        #     def get(field):
        #         idx = col_index_map.get(field)
        #         if idx is None or idx >= len(row):
        #             return None
        #         val = row[idx]
        #         return str(val).strip() if val is not None else None

        #     company_name = get("company_name")
        #     if not company_name:
        #         continue

        #     data = {
        #         "company_name": company_name,
        #         "pan_number": (get("pan_number") or ""),
        #         "contact_person": get("contact_person"),
        #         "contact_phone": get("contact_phone"),
        #         "contact_email": get("contact_email"),
        #     }

        #     serializer = BusinessSerializer(data=data)
        #     if serializer.is_valid():
        #         obj = Business.objects.create(**data)
        #         created.append(obj.company_name)
        #     else:
        #         errors.append({"row": row_num, "company_name": company_name, "errors": serializer.errors})

        # return Response(
        #     {
        #         "created_count": len(created),
        #         "created": created,
        #         "errors": errors,
        #     },
        #     status=status.HTTP_200_OK,
        # )


import openpyxl
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rent.models import Business
from user.models import Customer
from api.serializers.rent.business_using_slot import BusinessSerializer, BusinessBulkUploadSerializer

HEADER_MAP = {
    "company name": "company_name",
    "pan number": "pan_number",
    "contact person": "contact_person",
    "phone number": "contact_phone",
    "contact phone": "contact_phone",
    "email": "contact_email",
    "contact email": "contact_email",
}


class BusinessExcelUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        upload_serializer = BusinessBulkUploadSerializer(data=request.data)
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

        header_row_idx = None
        col_index_map = {}
        for i, row in enumerate(rows):
            normalized = [str(c).strip().lower() if c is not None else "" for c in row]
            if "company name" in normalized:
                header_row_idx = i
                for col_idx, header_text in enumerate(normalized):
                    field = HEADER_MAP.get(header_text)
                    if field:
                        col_index_map[field] = col_idx
                break

        if header_row_idx is None:
            return Response(
                {"detail": "Could not find a 'Company Name' header row in the sheet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "company_name" not in col_index_map:
            return Response(
                {"detail": "Company Name column is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, errors = [], []

        for row_num, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
            def get(field):
                idx = col_index_map.get(field)
                if idx is None or idx >= len(row):
                    return None
                val = row[idx]
                return str(val).strip() if val is not None else None

            company_name = get("company_name")
            if not company_name:
                continue

            data = {
                "company_name": company_name,
                "pan_number": (get("pan_number") or ""),
                "contact_person": get("contact_person"),
                "contact_phone": get("contact_phone"),
                "contact_email": get("contact_email"),
            }

            serializer = BusinessSerializer(data=data)
            if not serializer.is_valid():
                errors.append({"row": row_num, "company_name": company_name, "errors": serializer.errors})
                continue

            try:
                with transaction.atomic():
                    customer = Customer.objects.create(
                        name=company_name,
                        tax_number=data["pan_number"] or None,
                        contact_number=data["contact_phone"],
                        email=data["contact_email"],
                        created_by=request.user,
                    )
                    obj = Business.objects.create(**data, customer=customer)
                created.append(obj.company_name)
            except IntegrityError as e:
                errors.append({"row": row_num, "company_name": company_name, "errors": str(e)})

        return Response(
            {
                "created_count": len(created),
                "created": created,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )