# # # views.py

# # from decimal import Decimal

# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from rest_framework.permissions import IsAuthenticated
# # from django.db import transaction
# # from django.core.exceptions import ValidationError as DjangoValidationError

# # from bill.models import Bill
# # from rent.models import BillOtherItem
# # from organization.models import Branch
# # from bill.ird.postbillintoird import build_bill_ird_payload, postbillintoird
# # from bill.utils import finalize_other_bill_accounting

# # from api.serializers.rent.other_bill import OtherBillCreateSerializer


# # def _serialize_other_item(item):
# #     return {
# #         "item_name": item.item_name,
# #         "quantity": str(item.quantity),
# #         "rate": str(item.rate),
# #         "is_taxable": item.is_taxable,
# #         "subtotal": str(item.subtotal),
# #         "vat_amount": str(item.vat_amount),
# #         "total": str(item.total),
# #     }


# # class OtherBillCreateAPIView(APIView):
# #     """
# #     GET  /api/other-bills/create/
# #     POST /api/other-bills/create/
# #     {
# #         "customer": 12,
# #         "payment_mode": "Cash",
# #         "discount_amount": "500.00",
# #         "items": [
# #             {
# #                 "item_name": "Advertisement Banner",
# #                 "quantity": 1,
# #                 "rate": "5000.00",
# #                 "is_taxable": true
# #             },
# #             {
# #                 "item_name": "Design Service",
# #                 "quantity": 2,
# #                 "rate": "1500.00",
# #                 "is_taxable": false
# #             }
# #         ]
# #     }
# #     """
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         bills = (
# #             Bill.objects
# #             .filter(bill_type=Bill.BillType.OTHERS, is_deleted=False, status=True)
# #             .select_related('customer')
# #             .prefetch_related('other_details')
# #             .order_by('-transaction_date')
# #         )

# #         results = []
# #         for bill in bills:
# #             items = [i for i in bill.other_details.all() if not i.is_deleted]
# #             if not items:
# #                 continue

# #             results.append({
# #                 "bill_id": bill.id,
# #                 "invoice_number": bill.invoice_number,
# #                 "customer_id": bill.customer_id,
# #                 "customer_name": bill.customer_name,
# #                 "status": bill.status,
# #                 "grand_total": str(bill.grand_total),
# #                 "tax_amount": str(bill.tax_amount),
# #                 "taxable_amount": str(bill.taxable_amount),
# #                 "discount_amount": str(bill.discount_amount),
# #                 "items": [_serialize_other_item(item) for item in items],
# #             })

# #         return Response(results, status=status.HTTP_200_OK)

# #     def post(self, request):
# #         serializer = OtherBillCreateSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         data = serializer.validated_data

# #         branch = Branch.objects.order_by('id').first()
# #         if not branch:
# #             return Response(
# #                 {"error": "No branch configured in the system yet."},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         customer = data['customer']
# #         discount_amount = data.get('discount_amount') or Decimal('0.00')

# #         try:
# #             with transaction.atomic():
# #                 bill = Bill.objects.create(
# #                     agent=request.user,
# #                     bill_type=Bill.BillType.OTHERS,
# #                     customer=customer,
# #                     customer_name=customer.name,
# #                     customer_tax_number=customer.tax_number,
# #                     customer_address=customer.address,
# #                     branch=branch,
# #                     organization=getattr(branch, 'organization', None),
# #                     payment_mode=data.get('payment_mode', 'Cash'),
# #                     agent_name=request.user.username,
# #                 )

# #                 other_items = []
# #                 for item_data in data['items']:
# #                     other_item = BillOtherItem.objects.create(
# #                         bill=bill,
# #                         item_name=item_data['item_name'],
# #                         quantity=item_data.get('quantity', 1),
# #                         rate=item_data['rate'],
# #                         is_taxable=item_data.get('is_taxable', True),
# #                     )
# #                     other_items.append(other_item)

# #                 # Sum item totals first (no discount applied yet).
# #                 bill.recalculate_other_totals()

# #                 # Apply the flat, bill-level discount on top of the summed
# #                 # totals. Mirrors how the Sale flow treats discount_amount:
# #                 # it reduces grand_total but does NOT change taxable_amount/
# #                 # tax_amount, which stay based on items' full pre-discount
# #                 # value (discount is booked as a separate Discount Expense /
# #                 # Discount Sales journal pair, not folded into VAT).
# #                 if discount_amount > bill.grand_total:
# #                     raise DjangoValidationError(
# #                         f"Discount ({discount_amount}) cannot exceed the bill total ({bill.grand_total})."
# #                     )
# #                 bill.discount_amount = discount_amount
# #                 bill.grand_total = bill.grand_total - discount_amount
# #                 bill.save(update_fields=['discount_amount', 'grand_total'])

# #                 finalize_other_bill_accounting(bill)

# #                 # ---- Post to IRD now that totals are FINAL ----
# #                 try:
# #                     payload = build_bill_ird_payload(bill)
# #                     ird_response = postbillintoird(payload)
# #                     print(ird_response)
# #                 except Exception as e:
# #                     # Re-raise so transaction.atomic() rolls back this bill
# #                     # and its BillOtherItem rows -- we don't want a bill
# #                     # sitting in the DB that was never reported to IRD.
# #                     raise DjangoValidationError(
# #                         f"Failed to post bill to IRD: {e}"
# #                     )

# #                 result = {
# #                     "bill_id": bill.id,
# #                     "invoice_number": bill.invoice_number,
# #                     "customer_id": bill.customer_id,
# #                     "customer_name": bill.customer_name,
# #                     "grand_total": str(bill.grand_total),
# #                     "tax_amount": str(bill.tax_amount),
# #                     "taxable_amount": str(bill.taxable_amount),
# #                     "discount_amount": str(bill.discount_amount),
# #                     "items": [_serialize_other_item(item) for item in other_items],
# #                 }

# #         except DjangoValidationError as e:
# #             message = e.message_dict if hasattr(e, 'message_dict') else str(e)
# #             return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

# #         return Response({"bill": result}, status=status.HTTP_201_CREATED)


# # views.py

# from decimal import Decimal

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from django.db import transaction
# from django.core.exceptions import ValidationError as DjangoValidationError

# from bill.models import Bill
# from rent.models import BillOtherItem
# from organization.models import Branch
# from bill.ird.postbillintoird import build_bill_ird_payload, postbillintoird
# from bill.utils import finalize_other_bill_accounting

# from api.serializers.rent.other_bill import OtherBillCreateSerializer, OtherBillVoidSerializer


# def _serialize_other_item(item):
#     return {
#         "item_name": item.item_name,
#         "quantity": str(item.quantity),
#         "rate": str(item.rate),
#         "is_taxable": item.is_taxable,
#         "subtotal": str(item.subtotal),
#         "vat_amount": str(item.vat_amount),
#         "total": str(item.total),
#     }


# class OtherBillCreateAPIView(APIView):
#     """
#     GET  /api/other-bills/create/
#     POST /api/other-bills/create/
#     {
#         "customer": 12,
#         "payment_mode": "Cash",
#         "discount_amount": "500.00",
#         "items": [
#             {
#                 "item_name": "Advertisement Banner",
#                 "quantity": 1,
#                 "rate": "5000.00",
#                 "is_taxable": true
#             },
#             {
#                 "item_name": "Design Service",
#                 "quantity": 2,
#                 "rate": "1500.00",
#                 "is_taxable": false
#             }
#         ]
#     }
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         bills = (
#             Bill.objects
#             .filter(bill_type=Bill.BillType.OTHERS)
#             .select_related('customer')
#             .prefetch_related('other_details')
#             .order_by('-transaction_date')
#         )

#         results = []
#         for bill in bills:
#             items = [i for i in bill.other_details.all()]
#             if not items:
#                 continue

#             results.append({
#                 "bill_id": bill.id,
#                 "invoice_number": bill.invoice_number,
#                 "customer_id": bill.customer_id,
#                 "customer_name": bill.customer_name,
#                 "customer_tax_number": bill.customer_tax_number,
#                 "status": bill.status,
#                 "status": bill.status,
#                 "created_at": bill.created_at,
#                 "transaction_date": bill.transaction_date,
#                 "transaction_datetime": bill.transaction_date_time,
#                 "narration": bill.narration,
#                 "payment_mode": bill.payment_mode,
#                 "grand_total": str(bill.grand_total),
#                 "tax_amount": str(bill.tax_amount),
#                 "taxable_amount": str(bill.taxable_amount),
#                 "discount_amount": str(bill.discount_amount),
#                 "items": [_serialize_other_item(item) for item in items],
#             })

#         return Response(results, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = OtherBillCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data

#         branch = Branch.objects.order_by('id').first()
#         if not branch:
#             return Response(
#                 {"error": "No branch configured in the system yet."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         customer = data['customer']
#         discount_amount = data.get('discount_amount') or Decimal('0.00')
#         narration = data.get('narration', '')
#         try:
#             with transaction.atomic():
#                 bill = Bill.objects.create(
#                     agent=request.user,
#                     bill_type=Bill.BillType.OTHERS,
#                     customer=customer,
#                     customer_name=customer.name,
#                     customer_tax_number=customer.tax_number,
#                     customer_address=customer.address,
#                     branch=branch,
#                     organization=getattr(branch, 'organization', None),
#                     payment_mode=data.get('payment_mode', 'Cash'),
#                     agent_name=request.user.username,
#                     narration = narration
#                 )

#                 other_items = []
#                 for item_data in data['items']:
#                     other_item = BillOtherItem.objects.create(
#                         bill=bill,
#                         item_name=item_data['item_name'],
#                         quantity=item_data.get('quantity', 1),
#                         rate=item_data['rate'],
#                         is_taxable=item_data.get('is_taxable', True),
#                         subtotal=item_data['subtotal'],
#                         vat_amount=item_data['vat_amount'],
#                         total=item_data['total'],
#                     )
#                     other_items.append(other_item)

#                 # Bill-level totals now come from the frontend directly instead
#                 # of being summed from items server-side.
#                 bill.sub_total = data['sub_total']
#                 bill.taxable_amount = data['taxable_amount']
#                 bill.tax_amount = data['tax_amount']
#                 bill.grand_total = data['grand_total']

#                 # Apply the flat, bill-level discount on top of the
#                 # frontend-supplied grand_total. Mirrors how the Sale flow
#                 # treats discount_amount: it reduces grand_total but does NOT
#                 # change taxable_amount/tax_amount.
#                 if discount_amount > bill.grand_total:
#                     raise DjangoValidationError(
#                         f"Discount ({discount_amount}) cannot exceed the bill total ({bill.grand_total})."
#                     )
#                 bill.discount_amount = discount_amount
#                 bill.grand_total = bill.grand_total - discount_amount
#                 bill.save(update_fields=[
#                     'sub_total', 'taxable_amount', 'tax_amount',
#                     'discount_amount', 'grand_total',
#                 ])

#                 finalize_other_bill_accounting(bill)

#                 # ---- Post to IRD now that totals are FINAL ----
#                 try:
#                     payload = build_bill_ird_payload(bill)
#                     ird_response = postbillintoird(payload)
#                     print(ird_response)
#                 except Exception as e:
#                     raise DjangoValidationError(
#                         f"Failed to post bill to IRD: {e}"
#                     )

#                 result = {
#                     "bill_id": bill.id,
#                     "invoice_number": bill.invoice_number,
#                     "payment_mode": bill.payment_mode,

#                     "customer_id": bill.customer_id,
#                     "customer_name": bill.customer_name,
#                     "customer_tax_number": bill.customer_tax_number,

#                     "grand_total": str(bill.grand_total),
#                     "tax_amount": str(bill.tax_amount),
#                     "taxable_amount": str(bill.taxable_amount),
#                     "discount_amount": str(bill.discount_amount),
#                     "items": [_serialize_other_item(item) for item in other_items],
#                 }

#         except DjangoValidationError as e:
#             message = e.message_dict if hasattr(e, 'message_dict') else str(e)
#             return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({"bill": result}, status=status.HTTP_201_CREATED)


# from datetime import datetime

# from bill.models import Bill, TblTaxEntry, TablReturnEntry, IrdCredentials

# from rent.models import BillOtherItem
# from accounting.models import TblJournalEntry

# from accounting.views import create_reversing_journal_entry
# from nepali_datetime import date as nepali_date


# import logging
# from django.shortcuts import get_object_or_404
# logger = logging.getLogger(__name__)

# class OtherBillVoidAPIView(APIView):
#     """
#     POST /api/other-bills/void/
#     {
#         "bill_id": 42,
#         "reason": "Customer requested cancellation"
#     }
#     Voids an OTHERS bill only -- reverses its journal entry (and Others
#     subledger movement via create_reversing_journal_entry), posts an IRD
#     credit note, soft-deletes its BillOtherItem rows, and deactivates its
#     TblTaxEntry. Rejects any other bill_type; use MarkBillVoid for those.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = OtherBillVoidSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         bill_id = serializer.validated_data['bill_id']
#         reason = serializer.validated_data['reason']

#         bill = get_object_or_404(Bill, pk=bill_id)

#         if bill.bill_type != Bill.BillType.OTHERS:
#             return Response(
#                 {"error": f"Bill {bill_id} is a {bill.bill_type} bill, not an OTHERS bill. Use the appropriate void endpoint for it."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if not bill.status:
#             return Response(
#                 {"error": "This bill is already voided."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # ---------- STEP 1: Post credit note to IRD FIRST (before any DB writes) ----------
#         from bill.ird.postvoidbillintoird import post_credit_note_to_ird  # adjust import path as needed

#         if not bill.branch:
#             return Response(
#                 {"error": "Bill has no branch assigned; cannot determine IRD credentials."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         ird_creds = IrdCredentials.objects.first()
#         warnings = []
#         if not ird_creds:
#             logger.warning(f"No IRD credentials found for branch {bill.branch.branch_code}, skipping IRD post.")
#             warnings.append(f"No IRD credentials configured for outlet {bill.branch.branch_code}; skipped IRD posting.")
#         else:
#             ird_username = ird_creds.username
#             ird_password = ird_creds.password
#             ird_seller_pan = ird_creds.seller_pan

#             ad_date = bill.transaction_date
#             bs_date = nepali_date.from_datetime_date(ad_date)
#             bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

#             credit_note_payload = {
#                 "username": ird_username,
#                 "password": ird_password,
#                 "seller_pan": ird_seller_pan,
#                 "buyer_pan": "0",
#                 "fiscal_year": bill.fiscal_year,
#                 "buyer_name": bill.customer_name,
#                 "ref_invoice_number": f"{bill.invoice_number}",
#                 "credit_note_number": f"{bill.branch.branch_code}-VOID-{bill.invoice_number}",
#                 "credit_note_date": bs_date_str,
#                 "reason_for_return": reason if reason else "Voided Bill",
#                 "total_sales": float(bill.grand_total),
#                 # taxable_amount, not grand_total - tax_amount -- see the
#                 # is_taxable fix on recalculate_other_totals; grand_total -
#                 # tax_amount would wrongly include non-taxable items here.
#                 "taxable_sales_vat": float(bill.taxable_amount),
#                 "vat": float(bill.tax_amount),
#                 "excisable_amount": 0,
#                 "excise": 0,
#                 "taxable_sales_hst": 0,
#                 "hst": 0,
#                 "amount_for_esf": 0,
#                 "esf": 0,
#                 "export_sales": 0,
#                 "tax_exempted_sales": 0,
#                 "isrealtime": True,
#                 "datetimeClient": datetime.now().isoformat(),
#             }

#             try:
#                 post_credit_note_to_ird(credit_note_payload)
#             except Exception as e:
#                 logger.exception(f"Failed to post void credit note to IRD for bill {bill.invoice_number}")
#                 return Response(
#                     {"error": f"Failed to post credit note to IRD: {e}. Bill was NOT voided."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#         # ---------- STEP 2: IRD succeeded (or was skipped) -- now do all DB writes atomically ----------
#         try:
#             with transaction.atomic():
#                 reversing_journal_id = None
#                 try:
#                     journal_entry = TblJournalEntry.objects.get(bill_id=bill.id)
#                     reversing_journal = create_reversing_journal_entry(journal_entry.id, request.user.username)
#                     reversing_journal_id = reversing_journal.id
#                 except TblJournalEntry.DoesNotExist:
#                     warnings.append("No journal entry found to reverse.")
#                 except Exception as e:
#                     logger.exception(f"Error creating reversing journal entry for bill {bill.invoice_number}")
#                     warnings.append(f"Could not create reversing journal entry, but bill will be voided: {e}")

#                 bill.status = False
#                 bill.save(update_fields=['status'])

#                 quantity = bill.other_details.filter(is_deleted=False).count()

#                 TablReturnEntry.objects.create(
#                     bill_date=bill.transaction_date,
#                     bill_no=bill.invoice_number,
#                     customer_name=bill.customer_name,
#                     customer_pan=bill.customer_tax_number,
#                     amount=bill.grand_total,
#                     NoTaxSales=0,
#                     ZeroTaxSales=0,
#                     taxable_amount=bill.taxable_amount,
#                     tax_amount=bill.tax_amount,
#                     miti=bill.transaction_miti,
#                     ServicedItem="Others",
#                     quantity=quantity,
#                     reason=reason,
#                 )

#                 updated_count = bill.other_details.filter(is_deleted=False).update(is_deleted=True)
#                 logger.info(f"Soft-deleted {updated_count} BillOtherItem row(s) for voided others bill {bill.invoice_number}")

#                 try:
#                     entry = TblTaxEntry.objects.get(bill_no=bill.invoice_number, fiscal_year = bill.fiscal_year)
#                     entry.is_active = "NO"
#                     entry.save(update_fields=['is_active'])
#                 except TblTaxEntry.DoesNotExist:
#                     pass

#         except Exception as e:
#             logger.exception(f"Failed to void bill {bill.invoice_number} after IRD post succeeded")
#             return Response(
#                 {
#                     "error": (
#                         f"IRD credit note was posted, but voiding the bill failed and was rolled back: {e}. "
#                         f"A credit note may exist on IRD without a matching void -- contact support."
#                     )
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response(
#             {
#                 "bill_id": bill.id,
#                 "invoice_number": bill.invoice_number,
#                 "status": bill.status,
#                 "reversing_journal_id": reversing_journal_id,
#                 "items_voided": quantity,
#                 "warnings": warnings,
#             },
#             status=status.HTTP_200_OK,

#         )

# views.py

from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from bill.models import Bill
from rent.models import BillOtherItem
from organization.models import Branch
from bill.ird.postbillintoird import build_bill_ird_payload, postbillintoird
from bill.utils import finalize_other_bill_accounting, attempt_ird_sync, start_ird_retry_sweep
from django.utils import timezone

from api.serializers.rent.other_bill import OtherBillCreateSerializer, OtherBillVoidSerializer


def _serialize_other_item(item):
    return {
        "item_name": item.item_name,
        "quantity": str(item.quantity),
        "rate": str(item.rate),
        "is_taxable": item.is_taxable,
        "subtotal": str(item.subtotal),
        "vat_amount": str(item.vat_amount),
        "total": str(item.total),
    }

class OtherBillCreateAPIView(APIView):
    """
    GET  /api/other-bills/create/
    POST /api/other-bills/create/
    {
        "customer": 12,
        "payment_mode": "Cash",
        "discount_amount": "500.00",
        "items": [
            {
                "item_name": "Advertisement Banner",
                "quantity": 1,
                "rate": "5000.00",
                "is_taxable": true
            },
            {
                "item_name": "Design Service",
                "quantity": 2,
                "rate": "1500.00",
                "is_taxable": false
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bills = (
            Bill.objects
            .filter(bill_type=Bill.BillType.OTHERS)
            .select_related('customer')
            .prefetch_related('other_details')
            .order_by('-transaction_date')
        )

        results = []
        for bill in bills:
            items = [i for i in bill.other_details.all()]
            if not items:
                continue

            results.append({
                "bill_id": bill.id,
                "invoice_number": bill.invoice_number,
                "customer_id": bill.customer_id,
                "customer_name": bill.customer_name,
                "customer_tax_number": bill.customer_tax_number,
                "status": bill.status,
                "status": bill.status,
                "created_at": bill.created_at,
                "transaction_date": bill.transaction_date,
                "transaction_datetime": bill.transaction_date_time,
                "narration": bill.narration,
                "payment_mode": bill.payment_mode,
                "grand_total": str(bill.grand_total),
                "tax_amount": str(bill.tax_amount),
                "taxable_amount": str(bill.taxable_amount),
                "discount_amount": str(bill.discount_amount),
                "items": [_serialize_other_item(item) for item in items],
            })

        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OtherBillCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        branch = Branch.objects.order_by('id').first()
        if not branch:
            return Response(
                {"error": "No branch configured in the system yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = data['customer']
        discount_amount = data.get('discount_amount') or Decimal('0.00')
        narration = data.get('narration', '')

        try:
            with transaction.atomic():  # bill + items + ledger only -- no IRD here
                bill = Bill.objects.create(
                    agent=request.user,
                    bill_type=Bill.BillType.OTHERS,
                    customer=customer,
                    customer_name=customer.name,
                    customer_tax_number=customer.tax_number,
                    customer_address=customer.address,
                    branch=branch,
                    organization=getattr(branch, 'organization', None),
                    payment_mode=data.get('payment_mode', 'Cash'),
                    agent_name=request.user.username,
                    narration=narration,
                )
                if not bill.invoice_number:
                    raise DjangoValidationError(
                        "Failed to generate invoice number (possible duplicate collision) — please retry."
                    )

                other_items = []
                for item_data in data['items']:
                    other_item = BillOtherItem.objects.create(
                        bill=bill,
                        item_name=item_data['item_name'],
                        quantity=item_data.get('quantity', 1),
                        rate=item_data['rate'],
                        is_taxable=item_data.get('is_taxable', True),
                        subtotal=item_data['subtotal'],
                        vat_amount=item_data['vat_amount'],
                        total=item_data['total'],
                    )
                    other_items.append(other_item)

                # Bill-level totals come from the frontend directly instead of
                # being summed from items server-side.
                bill.sub_total = data['sub_total']
                bill.taxable_amount = data['taxable_amount']
                bill.tax_amount = data['tax_amount']
                bill.grand_total = data['grand_total']

                if discount_amount > bill.grand_total:
                    raise DjangoValidationError(
                        f"Discount ({discount_amount}) cannot exceed the bill total ({bill.grand_total})."
                    )
                bill.discount_amount = discount_amount
                # bill.grand_total = bill.grand_total - discount_amount
                bill.save(update_fields=[
                    'sub_total', 'taxable_amount', 'tax_amount',
                    'discount_amount', 'grand_total',
                ])

                finalize_other_bill_accounting(bill)
                # --- atomic block ends here: bill + BillOtherItem rows + ledger
                # entries are committed no matter what happens next. ---

            # IRD sync happens AFTER commit, outside any open transaction -- it
            # can never roll back the bill. attempt_ird_sync() already guards
            # against network/IRD errors internally and records the outcome on
            # the bill for the retry sweep to pick up later.
            try:
                attempt_ird_sync(bill)
            except Exception as e:
                # Only reachable for a genuine bug in the sync path itself --
                # the bill is already committed, so this must NOT turn into a
                # 400 that hides an otherwise-successful bill creation.
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
                    pass  # ird_synced was never flipped True -- retry sweep still catches it

            result = {
                "bill_id": bill.id,
                "invoice_number": bill.invoice_number,
                "payment_mode": bill.payment_mode,
                "customer_id": bill.customer_id,
                "customer_name": bill.customer_name,
                "customer_tax_number": bill.customer_tax_number,
                "grand_total": str(bill.grand_total),
                "tax_amount": str(bill.tax_amount),
                "taxable_amount": str(bill.taxable_amount),
                "discount_amount": str(bill.discount_amount),
                "ird_synced": bill.ird_synced,
                "ird_sync_error": bill.ird_sync_error,
                "items": [_serialize_other_item(item) for item in other_items],
            }

            # ---- Opportunistic retry of previously failed bills ----
            # Only if THIS bill synced successfully -- if IRD is currently
            # failing, don't bother sweeping old failures too.
            if bill.ird_synced:
                start_ird_retry_sweep(exclude_ids=[bill.id])

        except DjangoValidationError as e:
            # Reachable now only for genuine bill-creation failures -- bad
            # discount, missing data, invoice-number collision, etc. The bill
            # was never created, so there's truly nothing for this request.
            message = e.message_dict if hasattr(e, 'message_dict') else str(e)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"bill": result}, status=status.HTTP_201_CREATED)


from datetime import datetime

from bill.models import Bill, TblTaxEntry, TablReturnEntry, IrdCredentials

from rent.models import BillOtherItem
from accounting.models import TblJournalEntry

from accounting.views import create_reversing_journal_entry
from nepali_datetime import date as nepali_date


import logging
from django.shortcuts import get_object_or_404
logger = logging.getLogger(__name__)

class OtherBillVoidAPIView(APIView):
    """
    POST /api/other-bills/void/
    {
        "bill_id": 42,
        "reason": "Customer requested cancellation"
    }
    Voids an OTHERS bill only -- reverses its journal entry (and Others
    subledger movement via create_reversing_journal_entry), posts an IRD
    credit note, soft-deletes its BillOtherItem rows, and deactivates its
    TblTaxEntry. Rejects any other bill_type; use MarkBillVoid for those.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OtherBillVoidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bill_id = serializer.validated_data['bill_id']
        reason = serializer.validated_data['reason']

        bill = get_object_or_404(Bill, pk=bill_id)

        if bill.bill_type != Bill.BillType.OTHERS:
            return Response(
                {"error": f"Bill {bill_id} is a {bill.bill_type} bill, not an OTHERS bill. Use the appropriate void endpoint for it."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bill.status:
            return Response(
                {"error": "This bill is already voided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------- STEP 1: Post credit note to IRD FIRST (before any DB writes) ----------
        from bill.ird.postvoidbillintoird import post_credit_note_to_ird  # adjust import path as needed

        if not bill.branch:
            return Response(
                {"error": "Bill has no branch assigned; cannot determine IRD credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ird_creds = IrdCredentials.objects.first()
        warnings = []
        if not ird_creds:
            logger.warning(f"No IRD credentials found for branch {bill.branch.branch_code}, skipping IRD post.")
            warnings.append(f"No IRD credentials configured for outlet {bill.branch.branch_code}; skipped IRD posting.")
        else:
            ird_username = ird_creds.username
            ird_password = ird_creds.password
            ird_seller_pan = ird_creds.seller_pan

            ad_date = bill.transaction_date
            bs_date = nepali_date.from_datetime_date(ad_date)
            bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

            credit_note_payload = {
                "username": ird_username,
                "password": ird_password,
                "seller_pan": ird_seller_pan,
                "buyer_pan": "0",
                "fiscal_year": bill.fiscal_year,
                "buyer_name": bill.customer_name,
                "ref_invoice_number": f"{bill.invoice_number}",
                "credit_note_number": f"{bill.branch.branch_code}-VOID-{bill.invoice_number}",
                "credit_note_date": bs_date_str,
                "reason_for_return": reason if reason else "Voided Bill",
                "total_sales": float(bill.grand_total),
                # taxable_amount, not grand_total - tax_amount -- see the
                # is_taxable fix on recalculate_other_totals; grand_total -
                # tax_amount would wrongly include non-taxable items here.
                "taxable_sales_vat": float(bill.taxable_amount),
                "vat": float(bill.tax_amount),
                "excisable_amount": 0,
                "excise": 0,
                "taxable_sales_hst": 0,
                "hst": 0,
                "amount_for_esf": 0,
                "esf": 0,
                "export_sales": 0,
                "tax_exempted_sales": 0,
                "isrealtime": True,
                "datetimeClient": datetime.now().isoformat(),
            }

            # try:
            #     post_credit_note_to_ird(credit_note_payload)
            # except Exception as e:
            #     logger.exception(f"Failed to post void credit note to IRD for bill {bill.invoice_number}")
            #     return Response(
            #         {"error": f"Failed to post credit note to IRD: {e}. Bill was NOT voided."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            try:
                ird_response = post_credit_note_to_ird(credit_note_payload)
            except Exception as e:
                logger.exception(
                    f"Failed to post void credit note to IRD for bill {bill.invoice_number}"
                )
                return Response(
                    {"error": f"Failed to post credit note to IRD: {e}. Bill was NOT voided."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            logger.info(
                f"IRD credit note response for bill {bill.invoice_number}: "
                f"code={ird_response.get('code')} "
                f"message={ird_response.get('message')} "
                f"raw={ird_response.get('raw')!r}"
            )

            if not ird_response.get("success"):
                code = ird_response.get("code")
                if code is None:
                    detail = (
                        f"Could not reach IRD: {ird_response.get('message')}. "
                        f"Bill was NOT voided."
                    )
                    err_code = "ird_post_failed"
                else:
                    detail = (
                        f"IRD rejected the credit note: "
                        f"[{code}] {ird_response.get('message')}. "
                        f"Bill was NOT voided."
                    )
                    err_code = "ird_rejected"

                return Response(
                    {
                        "error": detail,
                        "code": err_code,
                        "ird_code": code,
                        "ird_message": ird_response.get("message"),
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        # ---------- STEP 2: IRD succeeded (or was skipped) -- now do all DB writes atomically ----------
        try:
            with transaction.atomic():
                reversing_journal_id = None
                try:
                    journal_entry = TblJournalEntry.objects.get(bill_id=bill.id)
                    reversing_journal = create_reversing_journal_entry(journal_entry.id, request.user.username)
                    reversing_journal_id = reversing_journal.id
                except TblJournalEntry.DoesNotExist:
                    warnings.append("No journal entry found to reverse.")
                except Exception as e:
                    logger.exception(f"Error creating reversing journal entry for bill {bill.invoice_number}")
                    warnings.append(f"Could not create reversing journal entry, but bill will be voided: {e}")

                bill.status = False
                bill.save(update_fields=['status'])

                quantity = bill.other_details.filter(is_deleted=False).count()

                TablReturnEntry.objects.create(
                    bill_date=bill.transaction_date,
                    bill_no=bill.invoice_number,
                    customer_name=bill.customer_name,
                    customer_pan=bill.customer_tax_number,
                    amount=bill.grand_total,
                    NoTaxSales=0,
                    ZeroTaxSales=0,
                    taxable_amount=bill.taxable_amount,
                    tax_amount=bill.tax_amount,
                    miti=bill.transaction_miti,
                    ServicedItem="Others",
                    quantity=quantity,
                    reason=reason,
                    fiscal_year=bill.fiscal_year,

                )

                updated_count = bill.other_details.filter(is_deleted=False).update(is_deleted=True)
                logger.info(f"Soft-deleted {updated_count} BillOtherItem row(s) for voided others bill {bill.invoice_number}")

                try:
                    entry = TblTaxEntry.objects.get(bill_no=bill.invoice_number, fiscal_year = bill.fiscal_year)
                    entry.is_active = "NO"
                    entry.save(update_fields=['is_active'])
                except TblTaxEntry.DoesNotExist:
                    pass

        except Exception as e:
            logger.exception(f"Failed to void bill {bill.invoice_number} after IRD post succeeded")
            return Response(
                {
                    "error": (
                        f"IRD credit note was posted, but voiding the bill failed and was rolled back: {e}. "
                        f"A credit note may exist on IRD without a matching void -- contact support."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "bill_id": bill.id,
                "invoice_number": bill.invoice_number,
                "status": bill.status,
                "reversing_journal_id": reversing_journal_id,
                "items_voided": quantity,
                "warnings": warnings,
            },
            status=status.HTTP_200_OK,

        )