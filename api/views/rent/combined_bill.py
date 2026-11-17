
# from decimal import Decimal

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from django.db import transaction
# from django.core.exceptions import ValidationError as DjangoValidationError
# from api.views.rent.other_bill import _serialize_other_item

# from bill.models import Bill

# def _serialize_rental_bill(bill):
#     rent_items = list(bill.rental_details.all())
#     total_rent = sum(item.rent_amount for item in rent_items)
#     rent_amounts = {item.rent_amount for item in rent_items}
#     same_rent_flag = len(rent_amounts) == 1
#     business = rent_items[0].contract.business if rent_items and rent_items[0].contract else None

#     return {
#         "bill_id": bill.id,
#         "print_count": bill.print_count,
#         "bill_type": bill.bill_type,
#         "invoice_number": bill.invoice_number,
#         "customer_id": bill.customer_id,
#         "business_name": bill.customer_name,
#         "status": bill.status,
#         "created_at": bill.created_at,
#         "transaction_date": bill.transaction_date,
#         "transaction_datetime": bill.transaction_date_time,
#         "payment_mode": bill.payment_mode,
#         "narration": bill.narration,
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
#         "non_taxable_amount": str(bill.grand_total - bill.tax_amount - bill.taxable_amount),
#         "discount_amount": str(bill.discount_amount),
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


# def _serialize_others_bill(bill):
#     items = list(bill.other_details.all())

#     return {
#         "bill_id": bill.id,
#         "print_count": bill.print_count,
#         "bill_type": "General" if bill.bill_type == "Others" else "General",
#         "invoice_number": bill.invoice_number,
#         "customer_id": bill.customer_id,
#         "customer_name": bill.customer_name,
#         "customer_tax_number": bill.customer_tax_number,
#         "status": bill.status,
#         "created_at": bill.created_at,
#         "transaction_date": bill.transaction_date,
#         "transaction_datetime": bill.transaction_date_time,
#         "narration": bill.narration,
#         "payment_mode": bill.payment_mode,
#         "grand_total": str(bill.grand_total),
#         "tax_amount": str(bill.tax_amount),
#         "taxable_amount": str(bill.taxable_amount),
#         "non_taxable_amount": str(bill.grand_total - bill.tax_amount - bill.taxable_amount),
#         "discount_amount": str(bill.discount_amount),
#         "items": [_serialize_other_item(item) for item in items],
#     }


# class CombinedRentalAndOtherBillListAPIView(APIView):
#     """
#     GET /api/bills/rental-and-other/?customer_id=12&business_id=1&bill_nepali_month=Shrawan&invoice_number=KT-1-58&start_date=2026-08-01&end_date=2026-08-31

#     Returns RENTAL and OTHERS bills merged into a single list, sorted by
#     transaction_date desc, so the frontend doesn't need to call two
#     endpoints and merge/sort them itself.

#     - customer_id: filters Bill.customer_id directly -- works for both
#       types, since a rental bill's customer is set to business.customer
#       at creation time (see BusinessRentalBillCreateAPIView.post).
#     - invoice_number: filters Bill.invoice_number directly -- works for
#       both types. Uses icontains rather than an exact match, since
#       invoice_number is not globally unique (unique_together with
#       fiscal_year + branch), so a partial/exact string still returns
#       every matching bill rather than erroring or assuming uniqueness.
#     - business_id / bill_nepali_month: only meaningful for RENTAL bills
#       (via rental_details__contract__business / rental_details__bill_nepali_month).
#       They're simply no-ops for OTHERS bills, not errors -- an OTHERS bill
#       never matches them and won't be excluded by them since the filter is
#       applied only within the RENTAL sub-query below.
#     - start_date / end_date: filters Bill.transaction_date for both types.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         customer_id = request.query_params.get('customer_id')
#         business_id = request.query_params.get('business_id')
#         bill_nepali_month = request.query_params.get('bill_nepali_month')
#         invoice_number = request.query_params.get('invoice_number')
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')

#         # ---- RENTAL bills ----
#         rental_bills = (
#             Bill.objects
#             .filter(bill_type=Bill.BillType.RENTAL)
#             .prefetch_related(
#                 'rental_details',
#                 'rental_details__slot',
#                 'rental_details__contract',
#                 'rental_details__contract__business',
#             )
#         )
#         rental_filter = {}
#         if business_id:
#             rental_filter['rental_details__contract__business_id'] = business_id
#         if bill_nepali_month:
#             rental_filter['rental_details__bill_nepali_month'] = bill_nepali_month
#         if rental_filter:
#             rental_bills = rental_bills.filter(**rental_filter)
#         if customer_id:
#             rental_bills = rental_bills.filter(customer_id=customer_id)
#         if invoice_number:
#             rental_bills = rental_bills.filter(invoice_number__icontains=invoice_number)
#         rental_bills = rental_bills.distinct()

#         # ---- OTHERS bills ----
#         other_bills = (
#             Bill.objects
#             .filter(bill_type=Bill.BillType.OTHERS)
#             .select_related('customer')
#             .prefetch_related('other_details')
#         )
#         if customer_id:
#             other_bills = other_bills.filter(customer_id=customer_id)
#         if invoice_number:
#             other_bills = other_bills.filter(invoice_number__icontains=invoice_number)

#         try:
#             if start_date:
#                 rental_bills = rental_bills.filter(transaction_date__gte=start_date)
#                 other_bills = other_bills.filter(transaction_date__gte=start_date)
#             if end_date:
#                 rental_bills = rental_bills.filter(transaction_date__lte=end_date)
#                 other_bills = other_bills.filter(transaction_date__lte=end_date)
#         except DjangoValidationError:
#             return Response(
#                 {"error": "start_date/end_date must be in YYYY-MM-DD format."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         results = []
#         for bill in rental_bills:
#             rent_items = list(bill.rental_details.all())
#             if not rent_items:
#                 continue
#             results.append(_serialize_rental_bill(bill))

#         for bill in other_bills:
#             items = list(bill.other_details.all())
#             if not items:
#                 continue
#             results.append(_serialize_others_bill(bill))

#         results.sort(key=lambda r: r["transaction_datetime"], reverse=True)

#         return Response(results, status=status.HTTP_200_OK)


from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from api.views.rent.other_bill import _serialize_other_item

from bill.models import Bill

def _serialize_rental_bill(bill):
    rent_items = list(bill.rental_details.all())
    total_rent = sum(item.rent_amount for item in rent_items)
    rent_amounts = {item.rent_amount for item in rent_items}
    same_rent_flag = len(rent_amounts) == 1
    business = rent_items[0].contract.business if rent_items and rent_items[0].contract else None

    return {
        "bill_id": bill.id,
        "print_count": bill.print_count,
        "bill_type": bill.bill_type,
        "invoice_number": bill.invoice_number,
        "customer_id": bill.customer_id,
        "business_name": bill.customer_name,
        "status": bill.status,
        "created_at": bill.created_at,
        "updated_at": bill.updated_at,
        "transaction_date": bill.transaction_date,
        "transaction_datetime": bill.transaction_date_time,
        "payment_mode": bill.payment_mode,
        "narration": bill.narration,
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
        "non_taxable_amount": str(bill.grand_total - bill.tax_amount - bill.taxable_amount),
        "discount_amount": str(bill.discount_amount),
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


def _serialize_others_bill(bill):
    items = list(bill.other_details.all())

    return {
        "bill_id": bill.id,
        "print_count": bill.print_count,
        "bill_type": "General" if bill.bill_type == "Others" else "General",
        "invoice_number": bill.invoice_number,
        "customer_id": bill.customer_id,
        "customer_name": bill.customer_name,
        "customer_tax_number": bill.customer_tax_number,
        "status": bill.status,
        "created_at": bill.created_at,
        "updated_at": bill.updated_at,
        "transaction_date": bill.transaction_date,
        "transaction_datetime": bill.transaction_date_time,
        "transaction_miti": bill.transaction_miti,
        "narration": bill.narration,
        "payment_mode": bill.payment_mode,
        "grand_total": str(bill.grand_total),
        "tax_amount": str(bill.tax_amount),
        "taxable_amount": str(bill.taxable_amount),
        "non_taxable_amount": str(bill.grand_total - bill.tax_amount - bill.taxable_amount),
        "discount_amount": str(bill.discount_amount),
        "items": [_serialize_other_item(item) for item in items],
    }

from datetime import datetime, time, timedelta, timezone

NEPAL_TZ = timezone(timedelta(hours=5, minutes=45))
UTC = timezone.utc


def nepali_date_range_to_utc(start_date_str, end_date_str):
    """
    start_date_str / end_date_str: 'YYYY-MM-DD' strings representing
    Nepal-local calendar dates (as picked by the user in the UI).

    Returns (start_utc, end_utc) tz-aware datetimes suitable for
    filtering a UTC-backed DateTimeField like BaseModel.updated_at
    (updated_at__gte=start_utc, updated_at__lte=end_utc).

    Raises ValueError if either string isn't valid YYYY-MM-DD.
    """
    start_utc = end_utc = None

    if start_date_str:
        d = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        start_local = datetime.combine(d, time.min, tzinfo=NEPAL_TZ)  # 00:00:00 NPT
        start_utc = start_local.astimezone(UTC)

    if end_date_str:
        d = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        end_local = datetime.combine(d, time.max, tzinfo=NEPAL_TZ)  # 23:59:59.999999 NPT
        end_utc = end_local.astimezone(UTC)

    return start_utc, end_utc


class CombinedRentalAndOtherBillListAPIView(APIView):
    """
    GET /api/bills/rental-and-other/?customer_id=12&business_id=1&bill_nepali_month=Shrawan&invoice_number=KT-1-58&start_date=2026-08-01&end_date=2026-08-31

    Returns RENTAL and OTHERS bills merged into a single list, sorted by
    transaction_date desc, so the frontend doesn't need to call two
    endpoints and merge/sort them itself.

    - customer_id: filters Bill.customer_id directly -- works for both
      types, since a rental bill's customer is set to business.customer
      at creation time (see BusinessRentalBillCreateAPIView.post).
    - invoice_number: filters Bill.invoice_number directly -- works for
      both types. Uses icontains rather than an exact match, since
      invoice_number is not globally unique (unique_together with
      fiscal_year + branch), so a partial/exact string still returns
      every matching bill rather than erroring or assuming uniqueness.
    - bill_nepali_month: for RENTAL bills, filters via
      rental_details__bill_nepali_month (exact match against the stored
      YYYY-MM-01 value). For OTHERS bills, filters via a YYYY-MM prefix
      match against Bill.transaction_miti, since OTHERS bills don't have
      a per-item nepali month -- only the bill-level transaction_miti.
    - business_id: only meaningful for RENTAL bills. It's a no-op for
      OTHERS bills, not an error -- an OTHERS bill never matches it and
      won't be excluded by it since the filter is applied only within
      the RENTAL sub-query below.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        business_id = request.query_params.get('business_id')
        bill_nepali_month = request.query_params.get('bill_nepali_month')
        invoice_number = request.query_params.get('invoice_number')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # ---- RENTAL bills ----
        rental_bills = (
            Bill.objects
            .filter(bill_type=Bill.BillType.RENTAL)
            .prefetch_related(
                'rental_details',
                'rental_details__slot',
                'rental_details__contract',
                'rental_details__contract__business',
            )
        )
        rental_filter = {}
        if business_id:
            rental_filter['rental_details__contract__business_id'] = business_id
        if bill_nepali_month:
            rental_filter['rental_details__bill_nepali_month'] = bill_nepali_month
        if rental_filter:
            rental_bills = rental_bills.filter(**rental_filter)
        if customer_id:
            rental_bills = rental_bills.filter(customer_id=customer_id)
        if invoice_number:
            rental_bills = rental_bills.filter(invoice_number__icontains=invoice_number)
        rental_bills = rental_bills.distinct()

        # ---- OTHERS bills ----
        other_bills = (
            Bill.objects
            .filter(bill_type=Bill.BillType.OTHERS)
            .select_related('customer')
            .prefetch_related('other_details')
        )
        if customer_id:
            other_bills = other_bills.filter(customer_id=customer_id)
        if invoice_number:
            other_bills = other_bills.filter(invoice_number__icontains=invoice_number)
        if bill_nepali_month:
            year_month_prefix = bill_nepali_month[:7]
            other_bills = other_bills.filter(transaction_miti__startswith=year_month_prefix)

        # try:
        #     if start_date:
        #         rental_bills = rental_bills.filter(transaction_date__gte=start_date)
        #         other_bills = other_bills.filter(transaction_date__gte=start_date)
        #     if end_date:
        #         rental_bills = rental_bills.filter(transaction_date__lte=end_date)
        #         other_bills = other_bills.filter(transaction_date__lte=end_date)

        # except (DjangoValidationError, ValueError):
        #     return Response(
        #         {"error": "start_date/end_date must be in YYYY-MM-DD format."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        try:
            start_utc, end_utc = nepali_date_range_to_utc(start_date, end_date)
            if start_utc:
                rental_bills = rental_bills.filter(updated_at__gte=start_utc)
                other_bills = other_bills.filter(updated_at__gte=start_utc)
            if end_utc:
                rental_bills = rental_bills.filter(updated_at__lte=end_utc)
                other_bills = other_bills.filter(updated_at__lte=end_utc)
        except ValueError:
            return Response(
                {"error": "start_date/end_date must be in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        for bill in rental_bills:
            rent_items = list(bill.rental_details.all())
            if not rent_items:
                continue
            results.append(_serialize_rental_bill(bill))

        for bill in other_bills:
            items = list(bill.other_details.all())
            if not items:
                continue
            results.append(_serialize_others_bill(bill))

        results.sort(key=lambda r: r["transaction_datetime"], reverse=True)

        return Response(results, status=status.HTTP_200_OK)