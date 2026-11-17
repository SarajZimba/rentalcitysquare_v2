# # views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from django.db import transaction
# from django.core.exceptions import ValidationError as DjangoValidationError

# from rent.models import BillRent
# from bill.models import Bill
# from organization.models import Branch
# from api.serializers.rent.rental_bill import BusinessRentalBillCreateSerializer, BillRentOutputSerializer, RentalBillListSerializer

# # views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from django.db import transaction
# from django.core.exceptions import ValidationError as DjangoValidationError

# from rent.models import BillRent
# from bill.models import Bill
# from organization.models import Branch
# from api.serializers.rent.rental_bill import (
#     MultiBusinessRentalBillCreateSerializer,
#     BillRentOutputSerializer,
#     RentalBillListSerializer,
# )

# from accounting.models import AccountLedger

# from bill.ird.postbillintoird import build_bill_ird_payload, postbillintoird

# from bill.utils import finalize_rental_bill_accounting, attempt_ird_sync, retry_previously_failed_ird_bills, start_ird_retry_sweep
# from django.utils import timezone
# class BusinessRentalBillCreateAPIView(APIView):
#     """
#     GET  /api/rental-bills/create/?business_id=1&start_date=2026-08-01&end_date=2026-08-31
#     POST /api/rental-bills/create/
#     {
#         "businesses": [
#             {
#                 "business": 1,
#                 "payment_mode": "Cash",
#                 "items": [
#                     {"slot": 3, "bill_month": "2026-08-01", "nea_current_unit": "465.00", "diesel_current_unit": "120.00", "ac_electricity_amount": "800.00"},
#                     {"slot": 5, "bill_month": "2026-08-01", "nea_current_unit": "300.00", "diesel_current_unit": "80.00", "ac_electricity_amount": "600.00"}
#                 ]
#             },
#             {
#                 "business": 2,
#                 "payment_mode": "Cash",
#                 "items": [
#                     {"slot": 8, "bill_month": "2026-08-01", "nea_current_unit": "220.00", "diesel_current_unit": "50.00", "ac_electricity_amount": "400.00"}
#                 ]
#             }
#         ]
#     }
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):


#         bills = (
#             Bill.objects
#             .filter(bill_type=Bill.BillType.RENTAL)
#             .prefetch_related(
#                 'rental_details',
#                 'rental_details__slot',
#                 'rental_details__contract',
#                 'rental_details__contract__business',
#             )
#             .order_by('-transaction_date')
#         )
 
#         business_id = request.query_params.get('business_id')
#         bill_nepali_month = request.query_params.get('bill_nepali_month')
 
#         # Build a single filter dict so both conditions apply against the
#         # SAME related rental_details row (one JOIN, not two).
#         rental_filter = {}
#         if business_id:
#             rental_filter['rental_details__contract__business_id'] = business_id
#         if bill_nepali_month:
#             rental_filter['rental_details__bill_nepali_month'] = bill_nepali_month
 
#         if rental_filter:
#             bills = bills.filter(**rental_filter)
 
#         # Always distinct at the end -- any join across a reverse/multi-valued
#         # relation (rental_details) can fan out one Bill into multiple rows.
#         bills = bills.distinct()

#         results = []
#         for bill in bills:
#             # rent_items = list(bill.rental_details.all())
#             rent_items = [i for i in bill.rental_details.all() if not i.is_deleted]
#             if not rent_items:
#                 continue
#             total_rent = sum(item.rent_amount for item in rent_items)
#             rent_amounts = {item.rent_amount for item in rent_items}
#             same_rent_flag = len(rent_amounts) == 1

#             # Business is the same across all items in a bill (one bill per business per submission)
#             business = rent_items[0].contract.business if rent_items[0].contract else None

#             results.append({
#                 "bill_id": bill.id,
#                 "invoice_number": bill.invoice_number,
#                 "business_name": bill.customer_name,
#                 "status": bill.status,
#                 "business": {
#                     "id": business.id,
#                     "company_name": business.company_name,
#                     "pan_number": business.pan_number,
#                     "contact_person": business.contact_person,
#                 } if business else None,
#                 "grand_total": str(bill.grand_total),
#                 "tax_amount": str(bill.tax_amount),
#                 "previous_due": str(bill.previous_due),
#                 "taxable_amount": str(bill.taxable_amount),
#                 "rent_summary": {
#                     "same_rent_for_all_slots": same_rent_flag,
#                     "rent_amount": str(total_rent),
#                     "slots": [
#                         {
#                             "slot": item.slot_id,
#                             "slot_number": item.slot.spaceno if item.slot else None,
#                             "floor": item.slot.floor if item.slot else None,
#                             "slot_status": item.slot.status if item.slot else None,
#                             "rent_amount": str(item.rent_amount),
#                         }
#                         for item in rent_items
#                     ],
#                 },
#                         "electricity_taxable_charges": [
#                             {
#                                 "slot": item.slot_id,
#                                 "slot_number": item.slot.spaceno,
#                                 "floor": item.slot.floor,
#                                 "nea_old_unit": str(item.nea_old_unit),
#                                 "nea_current_unit": str(item.nea_current_unit),
#                                 "nea_unit_diff": str(item.nea_unit_diff),
#                                 "nea_rate": str(item.nea_rate),
#                                 "nea_subtotal": str(item.nea_subtotal),
#                                 "diesel_old_unit": str(item.diesel_old_unit),
#                                 "diesel_current_unit": str(item.diesel_current_unit),
#                                 "diesel_unit_diff": str(item.diesel_unit_diff),
#                                 "diesel_rate": str(item.diesel_rate),
#                                 "diesel_subtotal": str(item.diesel_subtotal),
#                                 "bill_month": item.bill_month,
#                                 "bill_nepali_month": item.bill_nepali_month,
#                             }
#                             for item in rent_items
#                         ],
#                         "cam_taxable_charges": [
#                             {
#                                 "slot": item.slot_id,
#                                 "slot_number": item.slot.spaceno,
#                                 "floor": item.slot.floor,
#                                 "cam_amount": str(item.cam_amount),
#                                 "bill_month": item.bill_month,
#                                 "bill_nepali_month": item.bill_nepali_month,
#                             }
#                             for item in rent_items
#                         ],
#                         "ac_taxable_charges": [
#                             {
#                                 "slot": item.slot_id,
#                                 "slot_number": item.slot.spaceno,
#                                 "floor": item.slot.floor,
#                                 "ac_electricity_amount": str(item.ac_electricity_amount),
#                                 "bill_month": item.bill_month,
#                                 "bill_nepali_month": item.bill_nepali_month,
#                             }
#                             for item in rent_items
#                         ],
#             })

#         return Response(results, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = MultiBusinessRentalBillCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         business_groups = serializer.validated_data['businesses']

#         branch = Branch.objects.order_by('id').first()
#         if not branch:
#             return Response({"error": "No branch configured in the system yet."}, status=status.HTTP_400_BAD_REQUEST)

#         results = []
#         errors = []
#         created_bill_ids = []  # track bills created in THIS request
#         for group in business_groups:
#             business = group['business']
#             items_data = group['items']

#             try:
#                 with transaction.atomic():  # per-business savepoint -- bill + ledger only
#                     bill = Bill.objects.create(
#                         agent=request.user,
#                         bill_type=Bill.BillType.RENTAL,
#                         customer_name=business.company_name,
#                         customer_tax_number=business.pan_number,
#                         branch=branch,
#                         organization=getattr(branch, 'organization', None),
#                         payment_mode=group.get('payment_mode', 'Cash'),
#                         customer=business.customer,
#                         agent_name=request.user.username,
#                     )
#                     if not bill.invoice_number:
#                         raise DjangoValidationError(f"Failed to generate invoice number for {business.company_name} (possible duplicate collision) — please retry.")
#                     rent_items = []
#                     for item in items_data:
#                         rent_item = BillRent(
#                             agent=request.user,
#                             slot=item['slot'],
#                             contract=item['contract'],
#                             bill_month=item['bill_month'],
#                             bill_nepali_month=item['bill_nepali_month'],
#                             nea_current_unit=item['nea_current_unit'],
#                             diesel_current_unit=item['diesel_current_unit'],
#                             ac_electricity_amount=item['ac_electricity_amount'],
#                             bill=bill,
#                         )
#                         rent_item.save()
#                         rent_items.append(rent_item)

#                     bill.recalculate_rental_totals()

#                     from decimal import Decimal

#                     previous_due = Decimal('0')
#                     if business.customer:
#                         ledger_name = f'{business.customer.pk} - {business.customer.name}'
#                         ledger = AccountLedger.objects.filter(ledger_name=ledger_name).first()
#                         if ledger:
#                             previous_due = ledger.total_value
#                     bill.previous_due = previous_due
#                     bill.save(update_fields=['previous_due'])

#                     finalize_rental_bill_accounting(bill)
#                     # --- atomic block ends here: bill + BillRent rows + ledger
#                     # entries are committed no matter what happens next. ---
#                 created_bill_ids.append(bill.id)
#                 # IRD sync happens AFTER commit, outside any open transaction --
#                 # it can never roll back the bill itself. attempt_ird_sync()
#                 # already guards against network/IRD errors internally and
#                 # records the outcome on the bill for a later retry pass.
#                 try:
#                     attempt_ird_sync(bill)
#                 except Exception as e:
#                     # Only reachable for a genuine bug in the sync path itself
#                     # (e.g. build_bill_ird_payload throwing, a DB error updating
#                     # TblTaxEntry) -- the bill is already committed, so this must
#                     # NOT fall through to `errors` and get reported as if no
#                     # bill exists.
#                     bill.ird_synced = False
#                     bill.ird_sync_error = f"ird_sync_unexpected_error: {e}"
#                     bill.ird_last_attempt_at = timezone.now()
#                     bill.ird_retry_count = bill.ird_retry_count + 1
#                     try:
#                         bill.save(update_fields=[
#                             'ird_synced', 'ird_sync_error',
#                             'ird_last_attempt_at', 'ird_retry_count',
#                         ])
#                     except Exception:
#                         # Even if this bookkeeping save fails, ird_synced was
#                         # never flipped to True, so the retry task will still
#                         # pick this bill up -- nothing is silently lost.
#                         pass

#                 total_rent = sum(item.rent_amount for item in rent_items)
#                 rent_amounts = {item.rent_amount for item in rent_items}
#                 same_rent_flag = len(rent_amounts) == 1

#                 results.append({
#                     "bill_id": bill.id,
#                     "invoice_number": bill.invoice_number,
#                     "business_name": business.company_name,
#                     "tax_amount": str(bill.tax_amount),
#                     "taxable_amount": str(bill.taxable_amount),
#                     "previous_due": str(bill.previous_due),
#                     "ird_synced": bill.ird_synced,
#                     "ird_sync_error": bill.ird_sync_error,
#                     "business": {
#                         "id": business.id,
#                         "company_name": business.company_name,
#                         "pan_number": business.pan_number,
#                         "contact_person": business.contact_person,
#                     },
#                     "grand_total": str(bill.grand_total),
#                     "rent_summary": {
#                         "same_rent_for_all_slots": same_rent_flag,
#                         "rent_amount": str(total_rent),
#                         "slots": [
#                             {
#                                 "slot": item.slot_id,
#                                 "slot_number": item.slot.spaceno,
#                                 "floor": item.slot.floor,
#                                 "slot_status": item.slot.status,
#                                 "rent_amount": str(item.rent_amount),
#                             }
#                             for item in rent_items
#                         ],
#                     },
#                     "electricity_taxable_charges": [
#                         {
#                             "slot": item.slot_id,
#                             "slot_number": item.slot.spaceno,
#                             "floor": item.slot.floor,
#                             "nea_old_unit": str(item.nea_old_unit),
#                             "nea_current_unit": str(item.nea_current_unit),
#                             "nea_unit_diff": str(item.nea_unit_diff),
#                             "nea_rate": str(item.nea_rate),
#                             "nea_subtotal": str(item.nea_subtotal),
#                             "diesel_old_unit": str(item.diesel_old_unit),
#                             "diesel_current_unit": str(item.diesel_current_unit),
#                             "diesel_unit_diff": str(item.diesel_unit_diff),
#                             "diesel_rate": str(item.diesel_rate),
#                             "diesel_subtotal": str(item.diesel_subtotal),
#                             "bill_month": item.bill_month,
#                             "bill_nepali_month": item.bill_nepali_month,
#                         }
#                         for item in rent_items
#                     ],
#                     "cam_taxable_charges": [
#                         {
#                             "slot": item.slot_id,
#                             "slot_number": item.slot.spaceno,
#                             "floor": item.slot.floor,
#                             "cam_amount": str(item.cam_amount),
#                             "bill_month": item.bill_month,
#                             "bill_nepali_month": item.bill_nepali_month,
#                         }
#                         for item in rent_items
#                     ],
#                     "ac_taxable_charges": [
#                         {
#                             "slot": item.slot_id,
#                             "slot_number": item.slot.spaceno,
#                             "floor": item.slot.floor,
#                             "ac_electricity_amount": str(item.ac_electricity_amount),
#                             "bill_month": item.bill_month,
#                             "bill_nepali_month": item.bill_nepali_month,
#                         }
#                         for item in rent_items
#                     ],
#                 })

#             except DjangoValidationError as e:
#                 # Reachable now only for genuine bill-creation failures --
#                 # duplicate slot/month, missing contract, bad readings, etc.
#                 # The bill was never created, so there truly is nothing for
#                 # this business.
#                 message = e.message_dict if hasattr(e, 'message_dict') else str(e)
#                 errors.append({
#                     "business": business.id,
#                     "business_name": business.company_name,
#                     "error": message,
#                 })
#             except Exception as e:
#                 # Catch-all so one unexpected failure doesn't 500 the whole batch.
#                 errors.append({
#                     "business": business.id,
#                     "business_name": business.company_name,
#                     "error": str(e),
#                 })

#         # ---- Opportunistic retry of PREVIOUSLY failed bills ----
#         # Only runs if every bill created in THIS request synced to IRD
#         # successfully -- if IRD is currently failing, don't bother retrying
#         # old failures too, they'll just fail again and waste time.
#         all_current_synced = bool(results) and all(r["ird_synced"] for r in results)

#         if all_current_synced:
#             start_ird_retry_sweep(exclude_ids=created_bill_ids)

#         if errors and not results:
#             return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

#         if errors:
#             return Response({"bills": results, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

#         return Response({"bills": results}, status=status.HTTP_201_CREATED)


# def _serialize_rental_bill(bill):
#     """Shared by the list and detail rental-bill views so their output
#     for a single bill can never drift out of sync with each other."""
#     rent_items = [i for i in bill.rental_details.all() if not i.is_deleted]
#     total_rent = sum(item.rent_amount for item in rent_items)
#     rent_amounts = {item.rent_amount for item in rent_items}
#     same_rent_flag = len(rent_amounts) == 1

#     business = rent_items[0].contract.business if rent_items and rent_items[0].contract else None

#     return {
#         "bill_id": bill.id,
#         "invoice_number": bill.invoice_number,
#         "business_name": bill.customer_name,
#         "status": bill.status,
#         "business": {
#             "id": business.id,
#             "company_name": business.company_name,
#             "pan_number": business.pan_number,
#             "contact_person": business.contact_person,
#         } if business else None,
#         "grand_total": str(bill.grand_total),
#         "tax_amount": str(bill.tax_amount),
#         "previous_due": str(bill.previous_due),
#         "taxable_amount": str(bill.taxable_amount),
#         "rent_summary": {
#             "same_rent_for_all_slots": same_rent_flag,
#             "rent_amount": str(total_rent),
#             "slots": [
#                 {
#                     "slot": item.slot_id,
#                     "slot_number": item.slot.spaceno if item.slot else None,
#                     "floor": item.slot.floor if item.slot else None,
#                     "slot_status": item.slot.status if item.slot else None,
#                     "rent_amount": str(item.rent_amount),
#                 }
#                 for item in rent_items
#             ],
#         },
#         "electricity_taxable_charges": [
#             {
#                 "slot": item.slot_id,
#                 "slot_number": item.slot.spaceno,
#                 "floor": item.slot.floor,
#                 "nea_old_unit": str(item.nea_old_unit),
#                 "nea_current_unit": str(item.nea_current_unit),
#                 "nea_unit_diff": str(item.nea_unit_diff),
#                 "nea_rate": str(item.nea_rate),
#                 "nea_subtotal": str(item.nea_subtotal),
#                 "diesel_old_unit": str(item.diesel_old_unit),
#                 "diesel_current_unit": str(item.diesel_current_unit),
#                 "diesel_unit_diff": str(item.diesel_unit_diff),
#                 "diesel_rate": str(item.diesel_rate),
#                 "diesel_subtotal": str(item.diesel_subtotal),
#                 "bill_month": item.bill_month,
#                 "bill_nepali_month": item.bill_nepali_month,
#             }
#             for item in rent_items
#         ],
#         "cam_taxable_charges": [
#             {
#                 "slot": item.slot_id,
#                 "slot_number": item.slot.spaceno,
#                 "floor": item.slot.floor,
#                 "cam_amount": str(item.cam_amount),
#                 "bill_month": item.bill_month,
#                 "bill_nepali_month": item.bill_nepali_month,
#             }
#             for item in rent_items
#         ],
#         "ac_taxable_charges": [
#             {
#                 "slot": item.slot_id,
#                 "slot_number": item.slot.spaceno,
#                 "floor": item.slot.floor,
#                 "ac_electricity_amount": str(item.ac_electricity_amount),
#                 "bill_month": item.bill_month,
#                 "bill_nepali_month": item.bill_nepali_month,
#             }
#             for item in rent_items
#         ],
#     }

# from api.serializers.rent.rental_bill import RentalBillDetailLookupSerializer
# class RentalBillDetailAPIView(APIView):
#     """
#     POST /api/rental-bills/detail/
#     {
#         "invoice_number": "INV-2026-000123"
#     }
#     Returns the full rental-item breakdown for one bill, same shape as a
#     single entry from BusinessRentalBillCreateAPIView's list GET.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = RentalBillDetailLookupSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         invoice_number = serializer.validated_data['invoice_number']

#         try:
#             bill = (
#                 Bill.objects
#                 .filter(bill_type=Bill.BillType.RENTAL)
#                 .prefetch_related(
#                     'rental_details',
#                     'rental_details__slot',
#                     'rental_details__contract',
#                     'rental_details__contract__business',
#                 )
#                 .get(invoice_number=invoice_number)
#             )
#         except Bill.DoesNotExist:
#             return Response(
#                 {"error": f"No rental bill found with invoice number {invoice_number}."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         except Bill.MultipleObjectsReturned:
#             return Response(
#                 {"error": f"Multiple rental bills found with invoice number {invoice_number}; expected a unique match."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         rent_items = [i for i in bill.rental_details.all() if not i.is_deleted]
#         if not rent_items:
#             return Response(
#                 {"error": f"Bill with invoice number {invoice_number} has no active rental items."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         return Response(_serialize_rental_bill(bill), status=status.HTTP_200_OK)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rent.models import BillRent
from bill.models import Bill
from organization.models import Branch
from api.serializers.rent.rental_bill import BusinessRentalBillCreateSerializer, BillRentOutputSerializer, RentalBillListSerializer

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rent.models import BillRent
from bill.models import Bill
from organization.models import Branch
from api.serializers.rent.rental_bill import (
    MultiBusinessRentalBillCreateSerializer,
    BillRentOutputSerializer,
    RentalBillListSerializer,
)

from accounting.models import AccountLedger

from bill.ird.postbillintoird import build_bill_ird_payload, postbillintoird

from bill.utils import finalize_rental_bill_accounting, attempt_ird_sync, retry_previously_failed_ird_bills, start_ird_retry_sweep
from django.utils import timezone
class BusinessRentalBillCreateAPIView(APIView):
    """
    GET  /api/rental-bills/create/?business_id=1&start_date=2026-08-01&end_date=2026-08-31
    POST /api/rental-bills/create/
    {
        "businesses": [
            {
                "business": 1,
                "payment_mode": "Cash",
                "items": [
                    {"slot": 3, "bill_month": "2026-08-01", "nea_current_unit": "465.00", "diesel_current_unit": "120.00", "ac_electricity_amount": "800.00"},
                    {"slot": 5, "bill_month": "2026-08-01", "nea_current_unit": "300.00", "diesel_current_unit": "80.00", "ac_electricity_amount": "600.00"}
                ]
            },
            {
                "business": 2,
                "payment_mode": "Cash",
                "items": [
                    {"slot": 8, "bill_month": "2026-08-01", "nea_current_unit": "220.00", "diesel_current_unit": "50.00", "ac_electricity_amount": "400.00"}
                ]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):


        bills = (
            Bill.objects
            .filter(bill_type=Bill.BillType.RENTAL)
            .prefetch_related(
                'rental_details',
                'rental_details__slot',
                'rental_details__contract',
                'rental_details__contract__business',
            )
            .order_by('-transaction_date')
        )
 
        business_id = request.query_params.get('business_id')
        bill_nepali_month = request.query_params.get('bill_nepali_month')
 
        # Build a single filter dict so both conditions apply against the
        # SAME related rental_details row (one JOIN, not two).
        rental_filter = {}
        if business_id:
            rental_filter['rental_details__contract__business_id'] = business_id
        if bill_nepali_month:
            rental_filter['rental_details__bill_nepali_month'] = bill_nepali_month
 
        if rental_filter:
            bills = bills.filter(**rental_filter)
 
        # Always distinct at the end -- any join across a reverse/multi-valued
        # relation (rental_details) can fan out one Bill into multiple rows.
        bills = bills.distinct()

        results = []
        for bill in bills:
            # rent_items = list(bill.rental_details.all())
            rent_items = [i for i in bill.rental_details.all() if not i.is_deleted]
            if not rent_items:
                continue
            total_rent = sum(item.rent_amount for item in rent_items)
            rent_amounts = {item.rent_amount for item in rent_items}
            same_rent_flag = len(rent_amounts) == 1

            # Business is the same across all items in a bill (one bill per business per submission)
            business = rent_items[0].contract.business if rent_items[0].contract else None

            results.append({
                "bill_id": bill.id,
                "invoice_number": bill.invoice_number,
                "business_name": bill.customer_name,
                "status": bill.status,
                "business": {
                    "id": business.id,
                    "company_name": business.company_name,
                    "pan_number": business.pan_number,
                    "contact_person": business.contact_person,
                } if business else None,
                "grand_total": str(bill.grand_total),
                "tax_amount": str(bill.tax_amount),
                "previous_due": str(bill.previous_due),
                "taxable_amount": str(bill.taxable_amount),
                "rent_summary": {
                    "same_rent_for_all_slots": same_rent_flag,
                    "rent_amount": str(total_rent),
                    "slots": [
                        {
                            "slot": item.slot_id,
                            "slot_number": item.slot.spaceno if item.slot else None,
                            "floor": item.slot.floor if item.slot else None,
                            "slot_status": item.slot.status if item.slot else None,
                            "rent_amount": str(item.rent_amount),
                        }
                        for item in rent_items
                    ],
                },
                        "electricity_taxable_charges": [
                            {
                                "slot": item.slot_id,
                                "slot_number": item.slot.spaceno,
                                "floor": item.slot.floor,
                                "nea_old_unit": str(item.nea_old_unit),
                                "nea_current_unit": str(item.nea_current_unit),
                                "nea_unit_diff": str(item.nea_unit_diff),
                                "nea_rate": str(item.nea_rate),
                                "nea_subtotal": str(item.nea_subtotal),
                                "diesel_old_unit": str(item.diesel_old_unit),
                                "diesel_current_unit": str(item.diesel_current_unit),
                                "diesel_unit_diff": str(item.diesel_unit_diff),
                                "diesel_rate": str(item.diesel_rate),
                                "diesel_subtotal": str(item.diesel_subtotal),
                                "bill_month": item.bill_month,
                                "bill_nepali_month": item.bill_nepali_month,
                            }
                            for item in rent_items
                        ],
                        "cam_taxable_charges": [
                            {
                                "slot": item.slot_id,
                                "slot_number": item.slot.spaceno,
                                "floor": item.slot.floor,
                                "cam_amount": str(item.cam_amount),
                                "bill_month": item.bill_month,
                                "bill_nepali_month": item.bill_nepali_month,
                            }
                            for item in rent_items
                        ],
                        "ac_taxable_charges": [
                            {
                                "slot": item.slot_id,
                                "slot_number": item.slot.spaceno,
                                "floor": item.slot.floor,
                                "ac_electricity_amount": str(item.ac_electricity_amount),
                                "bill_month": item.bill_month,
                                "bill_nepali_month": item.bill_nepali_month,
                            }
                            for item in rent_items
                        ],
            })

        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MultiBusinessRentalBillCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business_groups = serializer.validated_data['businesses']

        branch = Branch.objects.order_by('id').first()
        if not branch:
            return Response({"error": "No branch configured in the system yet."}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []
        created_bill_ids = []  # track bills created in THIS request
        for group in business_groups:
            business = group['business']
            items_data = group['items']

            try:
                with transaction.atomic():  # per-business savepoint -- bill + ledger only
                    bill = Bill.objects.create(
                        agent=request.user,
                        bill_type=Bill.BillType.RENTAL,
                        customer_name=business.company_name,
                        customer_tax_number=business.pan_number,
                        branch=branch,
                        organization=getattr(branch, 'organization', None),
                        payment_mode=group.get('payment_mode', 'Cash'),
                        customer=business.customer,
                        agent_name=request.user.username,
                    )
                    if not bill.invoice_number:
                        raise DjangoValidationError(f"Failed to generate invoice number for {business.company_name} (possible duplicate collision) — please retry.")
                    rent_items = []
                    for item in items_data:
                        # rent_item = BillRent(
                        #     agent=request.user,
                        #     slot=item['slot'],
                        #     contract=item['contract'],
                        #     bill_month=item['bill_month'],
                        #     bill_nepali_month=item['bill_nepali_month'],
                        #     nea_current_unit=item['nea_current_unit'],
                        #     diesel_current_unit=item['diesel_current_unit'],
                        #     ac_electricity_amount=item['ac_electricity_amount'],
                        #     bill=bill,
                        # )
                        # rent_item.save()
                        # rent_items.append(rent_item)

                        rent_item = BillRent(
                            agent=request.user,
                            slot=item['slot'],
                            contract=item['contract'],
                            bill_month=item['bill_month'],
                            bill_nepali_month=item['bill_nepali_month'],
                            nea_old_unit=item['nea_old_unit'],
                            nea_current_unit=item['nea_current_unit'],
                            diesel_old_unit=item['diesel_old_unit'],
                            diesel_current_unit=item['diesel_current_unit'],
                            ac_electricity_amount=item['ac_electricity_amount'],
                            bill=bill,
                        )
                        rent_item.save()
                        rent_items.append(rent_item)

                    bill.recalculate_rental_totals()

                    from decimal import Decimal

                    previous_due = Decimal('0')
                    if business.customer:
                        ledger_name = f'{business.customer.pk} - {business.customer.name}'
                        ledger = AccountLedger.objects.filter(ledger_name=ledger_name).first()
                        if ledger:
                            previous_due = ledger.total_value
                    bill.previous_due = previous_due
                    bill.save(update_fields=['previous_due'])

                    finalize_rental_bill_accounting(bill)
                    # --- atomic block ends here: bill + BillRent rows + ledger
                    # entries are committed no matter what happens next. ---
                created_bill_ids.append(bill.id)
                # IRD sync happens AFTER commit, outside any open transaction --
                # it can never roll back the bill itself. attempt_ird_sync()
                # already guards against network/IRD errors internally and
                # records the outcome on the bill for a later retry pass.
                try:
                    attempt_ird_sync(bill)
                except Exception as e:
                    # Only reachable for a genuine bug in the sync path itself
                    # (e.g. build_bill_ird_payload throwing, a DB error updating
                    # TblTaxEntry) -- the bill is already committed, so this must
                    # NOT fall through to `errors` and get reported as if no
                    # bill exists.
                    bill.ird_synced = False
                    bill.ird_sync_error = f"ird_sync_unexpected_error: {e}"
                    bill.ird_last_attempt_at = timezone.now()
                    bill.ird_retry_count = bill.ird_retry_count + 1
                    try:
                        bill.save(update_fields=[
                            'ird_synced', 'ird_sync_error',
                            'ird_last_attempt_at', 'ird_retry_count',
                        ])
                    except Exception:
                        # Even if this bookkeeping save fails, ird_synced was
                        # never flipped to True, so the retry task will still
                        # pick this bill up -- nothing is silently lost.
                        pass

                total_rent = sum(item.rent_amount for item in rent_items)
                rent_amounts = {item.rent_amount for item in rent_items}
                same_rent_flag = len(rent_amounts) == 1

                results.append({
                    "bill_id": bill.id,
                    "invoice_number": bill.invoice_number,
                    "business_name": business.company_name,
                    "tax_amount": str(bill.tax_amount),
                    "taxable_amount": str(bill.taxable_amount),
                    "previous_due": str(bill.previous_due),
                    "ird_synced": bill.ird_synced,
                    "ird_sync_error": bill.ird_sync_error,
                    "business": {
                        "id": business.id,
                        "company_name": business.company_name,
                        "pan_number": business.pan_number,
                        "contact_person": business.contact_person,
                    },
                    "grand_total": str(bill.grand_total),
                    "rent_summary": {
                        "same_rent_for_all_slots": same_rent_flag,
                        "rent_amount": str(total_rent),
                        "slots": [
                            {
                                "slot": item.slot_id,
                                "slot_number": item.slot.spaceno,
                                "floor": item.slot.floor,
                                "slot_status": item.slot.status,
                                "rent_amount": str(item.rent_amount),
                            }
                            for item in rent_items
                        ],
                    },
                    "electricity_taxable_charges": [
                        {
                            "slot": item.slot_id,
                            "slot_number": item.slot.spaceno,
                            "floor": item.slot.floor,
                            "nea_old_unit": str(item.nea_old_unit),
                            "nea_current_unit": str(item.nea_current_unit),
                            "nea_unit_diff": str(item.nea_unit_diff),
                            "nea_rate": str(item.nea_rate),
                            "nea_subtotal": str(item.nea_subtotal),
                            "diesel_old_unit": str(item.diesel_old_unit),
                            "diesel_current_unit": str(item.diesel_current_unit),
                            "diesel_unit_diff": str(item.diesel_unit_diff),
                            "diesel_rate": str(item.diesel_rate),
                            "diesel_subtotal": str(item.diesel_subtotal),
                            "bill_month": item.bill_month,
                            "bill_nepali_month": item.bill_nepali_month,
                        }
                        for item in rent_items
                    ],
                    "cam_taxable_charges": [
                        {
                            "slot": item.slot_id,
                            "slot_number": item.slot.spaceno,
                            "floor": item.slot.floor,
                            "cam_amount": str(item.cam_amount),
                            "bill_month": item.bill_month,
                            "bill_nepali_month": item.bill_nepali_month,
                        }
                        for item in rent_items
                    ],
                    "ac_taxable_charges": [
                        {
                            "slot": item.slot_id,
                            "slot_number": item.slot.spaceno,
                            "floor": item.slot.floor,
                            "ac_electricity_amount": str(item.ac_electricity_amount),
                            "bill_month": item.bill_month,
                            "bill_nepali_month": item.bill_nepali_month,
                        }
                        for item in rent_items
                    ],
                })

            except DjangoValidationError as e:
                # Reachable now only for genuine bill-creation failures --
                # duplicate slot/month, missing contract, bad readings, etc.
                # The bill was never created, so there truly is nothing for
                # this business.
                message = e.message_dict if hasattr(e, 'message_dict') else str(e)
                errors.append({
                    "business": business.id,
                    "business_name": business.company_name,
                    "error": message,
                })
            except Exception as e:
                # Catch-all so one unexpected failure doesn't 500 the whole batch.
                errors.append({
                    "business": business.id,
                    "business_name": business.company_name,
                    "error": str(e),
                })

        # ---- Opportunistic retry of PREVIOUSLY failed bills ----
        # Only runs if every bill created in THIS request synced to IRD
        # successfully -- if IRD is currently failing, don't bother retrying
        # old failures too, they'll just fail again and waste time.
        all_current_synced = bool(results) and all(r["ird_synced"] for r in results)

        if all_current_synced:
            start_ird_retry_sweep(exclude_ids=created_bill_ids)

        if errors and not results:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        if errors:
            return Response({"bills": results, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

        return Response({"bills": results}, status=status.HTTP_201_CREATED)


def _serialize_rental_bill(bill):
    """Shared by the list and detail rental-bill views so their output
    for a single bill can never drift out of sync with each other."""
    rent_items = [i for i in bill.rental_details.all() if not i.is_deleted]
    total_rent = sum(item.rent_amount for item in rent_items)
    rent_amounts = {item.rent_amount for item in rent_items}
    same_rent_flag = len(rent_amounts) == 1

    business = rent_items[0].contract.business if rent_items and rent_items[0].contract else None

    return {
        "bill_id": bill.id,
        "invoice_number": bill.invoice_number,
        "business_name": bill.customer_name,
        "status": bill.status,
        "business": {
            "id": business.id,
            "company_name": business.company_name,
            "pan_number": business.pan_number,
            "contact_person": business.contact_person,
        } if business else None,
        "grand_total": str(bill.grand_total),
        "tax_amount": str(bill.tax_amount),
        "previous_due": str(bill.previous_due),
        "taxable_amount": str(bill.taxable_amount),
        "rent_summary": {
            "same_rent_for_all_slots": same_rent_flag,
            "rent_amount": str(total_rent),
            "slots": [
                {
                    "slot": item.slot_id,
                    "slot_number": item.slot.spaceno if item.slot else None,
                    "floor": item.slot.floor if item.slot else None,
                    "slot_status": item.slot.status if item.slot else None,
                    "rent_amount": str(item.rent_amount),
                }
                for item in rent_items
            ],
        },
        "electricity_taxable_charges": [
            {
                "slot": item.slot_id,
                "slot_number": item.slot.spaceno,
                "floor": item.slot.floor,
                "nea_old_unit": str(item.nea_old_unit),
                "nea_current_unit": str(item.nea_current_unit),
                "nea_unit_diff": str(item.nea_unit_diff),
                "nea_rate": str(item.nea_rate),
                "nea_subtotal": str(item.nea_subtotal),
                "diesel_old_unit": str(item.diesel_old_unit),
                "diesel_current_unit": str(item.diesel_current_unit),
                "diesel_unit_diff": str(item.diesel_unit_diff),
                "diesel_rate": str(item.diesel_rate),
                "diesel_subtotal": str(item.diesel_subtotal),
                "bill_month": item.bill_month,
                "bill_nepali_month": item.bill_nepali_month,
            }
            for item in rent_items
        ],
        "cam_taxable_charges": [
            {
                "slot": item.slot_id,
                "slot_number": item.slot.spaceno,
                "floor": item.slot.floor,
                "cam_amount": str(item.cam_amount),
                "bill_month": item.bill_month,
                "bill_nepali_month": item.bill_nepali_month,
            }
            for item in rent_items
        ],
        "ac_taxable_charges": [
            {
                "slot": item.slot_id,
                "slot_number": item.slot.spaceno,
                "floor": item.slot.floor,
                "ac_electricity_amount": str(item.ac_electricity_amount),
                "bill_month": item.bill_month,
                "bill_nepali_month": item.bill_nepali_month,
            }
            for item in rent_items
        ],
    }

from api.serializers.rent.rental_bill import RentalBillDetailLookupSerializer
class RentalBillDetailAPIView(APIView):
    """
    POST /api/rental-bills/detail/
    {
        "invoice_number": "INV-2026-000123"
    }
    Returns the full rental-item breakdown for one bill, same shape as a
    single entry from BusinessRentalBillCreateAPIView's list GET.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RentalBillDetailLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice_number = serializer.validated_data['invoice_number']

        try:
            bill = (
                Bill.objects
                .filter(bill_type=Bill.BillType.RENTAL)
                .prefetch_related(
                    'rental_details',
                    'rental_details__slot',
                    'rental_details__contract',
                    'rental_details__contract__business',
                )
                .get(invoice_number=invoice_number)
            )
        except Bill.DoesNotExist:
            return Response(
                {"error": f"No rental bill found with invoice number {invoice_number}."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Bill.MultipleObjectsReturned:
            return Response(
                {"error": f"Multiple rental bills found with invoice number {invoice_number}; expected a unique match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rent_items = [i for i in bill.rental_details.all() if not i.is_deleted]
        if not rent_items:
            return Response(
                {"error": f"Bill with invoice number {invoice_number} has no active rental items."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(_serialize_rental_bill(bill), status=status.HTTP_200_OK)