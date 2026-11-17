# from datetime import date as _date
# from django.db import transaction
# from nepali_datetime import date as nepali_date
# from rest_framework import serializers, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from bill.models import TblSalesEntry, TablReturnEntry
# from accounting.views import create_reversing_journal_entry
# from api.serializers.hotel.hotelbillvoid import HotelBillVoidSerializer
# import logging

# logger = logging.getLogger(__name__)

# class HotelBillVoidAPIView(APIView):
#     """
#     POST /api/hotel-bills/void/
#     { "bill_no": "15", "bill_date": "2026-10-01", "reason": "Wrong guest billed" }
#     Finds the sales entry by date + bill no, reverses its linked journal
#     and writes a TablReturnEntry.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = HotelBillVoidSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         bill_no = serializer.validated_data['bill_no']
#         bill_date = serializer.validated_data['bill_date'].strftime('%Y-%m-%d')
#         reason = serializer.validated_data['reason'] or "Voided Bill"

#         try:
#             with transaction.atomic():
#                 # row lock: two simultaneous voids of the same bill run one after the other
#                 entries = TblSalesEntry.objects.select_for_update().filter(
#                     bill_date=bill_date, bill_no=bill_no
#                 )
#                 if not entries.exists():
#                     return Response(
#                         {"error": f"No sales entry found for bill {bill_no} on {bill_date}."},
#                         status=status.HTTP_404_NOT_FOUND,
#                     )

#                 entry = entries.filter(journal_entry__isnull=False).first()
#                 if entry is None:
#                     return Response(
#                         {"error": f"Sales entry for bill {bill_no} has no linked journal entry, so it cannot be reversed automatically."},
#                         status=status.HTTP_409_CONFLICT,
#                     )

#                 # already voided? the return entry is the record of it
#                 if TablReturnEntry.objects.filter(
#                     bill_no=entry.bill_no,
#                     amount=entry.amount,
#                     tax_amount=entry.tax_amount,
#                     customer_name=entry.customer_name,
#                 ).exists():
#                     return Response(
#                         {"error": "This bill is already voided."},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 reversing_journal = create_reversing_journal_entry(
#                     entry.journal_entry_id, request.user.username
#                 )

#                 today = _date.today()
#                 today_bs = nepali_date.from_datetime_date(today)
#                 TablReturnEntry.objects.create(
#                     bill_date=today,
#                     bill_no=entry.bill_no,
#                     customer_name=entry.customer_name,
#                     customer_pan=entry.customer_pan,
#                     amount=entry.amount,
#                     NoTaxSales=entry.NoTaxSales,
#                     ZeroTaxSales=entry.ZeroTaxSales,
#                     taxable_amount=entry.taxable_amount,
#                     tax_amount=entry.tax_amount,
#                     miti=f"{today_bs.year}.{today_bs.month:02d}.{today_bs.day:02d}",
#                     ServicedItem=entry.ServicedItem,
#                     quantity=entry.quantity,
#                     reason=reason,
#                 )

#         except Exception as e:
#             logger.exception(f"Failed to void hotel bill {bill_no} ({bill_date})")
#             return Response(
#                 {"error": f"Could not void bill {bill_no}: {e}. Nothing was changed."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response(
#             {
#                 "bill_no": entry.bill_no,
#                 "bill_date": bill_date,
#                 "journal_entry_id": entry.journal_entry_id,
#                 "reversing_journal_id": reversing_journal.id,
#                 "voided": True,
#             },
#             status=status.HTTP_200_OK,
#         )


import logging
from datetime import date as _date, datetime

from django.db import transaction
from nepali_datetime import date as nepali_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bill.models import TblSalesEntry, TblTaxEntry, TablReturnEntry, BillIndex
from accounting.views import create_reversing_journal_entry
from api.serializers.hotel.hotelbillvoid import HotelBillVoidSerializer
# adjust these two imports to where they live in your project
from bill.ird.postvoidbillintoird import post_credit_note_to_ird
from bill.models import IrdCredentials

logger = logging.getLogger(__name__)


def _bs_str(d):
    bs = nepali_date.from_datetime_date(d)
    return f"{bs.year}.{bs.month:02d}.{bs.day:02d}"


def _to_date(value):
    """TblSalesEntry.bill_date may be a str, datetime or date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, _date):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def _already_voided(entry):
    return TablReturnEntry.objects.filter(
        bill_no=entry.bill_no,
        amount=entry.amount,
        tax_amount=entry.tax_amount,
        customer_name=entry.customer_name,
    ).exists()


# class HotelBillVoidAPIView(APIView):
#     """
#     POST /api/hotel-bills/void/
#     { "bill_no": "01-2-15", "bill_date": "2026-10-01",
#       "fiscal_year": "2083/84", "reason": "Wrong guest billed" }

#     1. Read-only checks (entry exists, has journal, not already voided, synced to IRD)
#     2. Post credit note to IRD (before any DB write)
#     3. Atomically: reverse journal, write TablReturnEntry, deactivate TblTaxEntry
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = HotelBillVoidSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         bill_no = serializer.validated_data['bill_no']
#         bill_date = serializer.validated_data['bill_date'].strftime('%Y-%m-%d')
#         fiscal_year = serializer.validated_data.get('fiscal_year')
#         reason = serializer.validated_data.get('reason') or "Voided Bill"

#         # ---------- STEP 1: read-only checks ----------
#         qs = TblSalesEntry.objects.filter(bill_date=bill_date, bill_no=bill_no)
#         if fiscal_year:
#             qs = qs.filter(fiscal_year=fiscal_year)
#         entry = qs.filter(journal_entry__isnull=False).first()

#         if entry is None:
#             if qs.exists():
#                 return Response(
#                     {"error": f"Sales entry for bill {bill_no} has no linked journal entry, "
#                               f"so it cannot be reversed automatically."},
#                     status=status.HTTP_409_CONFLICT,
#                 )
#             return Response(
#                 {"error": f"No sales entry found for bill {bill_no} on {bill_date}."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         if _already_voided(entry):
#             return Response({"error": "This bill is already voided."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         tax_entry = TblTaxEntry.objects.filter(
#             bill_no=entry.bill_no, fiscal_year=entry.fiscal_year
#         ).first()

#         # IRD rejects a credit note for an invoice it never received
#         if tax_entry is not None and tax_entry.sync_with_ird != "Yes":
#             return Response(
#                 {
#                     "error": "The original bill has not been synced to IRD yet, so a credit note "
#                              "cannot be posted. Wait for the sync to complete and try again.",
#                     "code": "ORIGINAL_NOT_SYNCED",
#                 },
#                 status=status.HTTP_409_CONFLICT,
#             )

#         # ---------- STEP 2: credit note to IRD FIRST ----------
#         warnings = []
#         ird_posted = False
#         ird_creds = IrdCredentials.objects.first()

#         if not ird_creds:
#             logger.warning("No IRD credentials found, skipping IRD credit note for hotel bill %s",
#                            entry.bill_no)
#             warnings.append("No IRD credentials configured; skipped IRD posting.")
#         else:
#             Branch = BillIndex._meta.get_field('branch').related_model
#             branch = Branch.objects.first()
#             if not branch:
#                 return Response(
#                     {"error": "No branch configured; cannot build credit note number."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # same as the others void: credit note date = ORIGINAL bill date, in BS
#             bs_date_str = _bs_str(_to_date(entry.bill_date))

#             credit_note_payload = {
#                 "username": ird_creds.username,
#                 "password": ird_creds.password,
#                 "seller_pan": ird_creds.seller_pan,
#                 "buyer_pan": "0",
#                 "fiscal_year": entry.fiscal_year,
#                 "buyer_name": entry.customer_name,
#                 "ref_invoice_number": f"{entry.bill_no}",
#                 "credit_note_number": f"{branch.branch_code}-VOID-{entry.bill_no}",
#                 "credit_note_date": bs_date_str,
#                 "reason_for_return": reason if reason else "Voided Bill",
#                 "total_sales": float(entry.amount),
#                 "taxable_sales_vat": float(entry.taxable_amount),
#                 "vat": float(entry.tax_amount),
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
#                 ird_response = post_credit_note_to_ird(credit_note_payload)
#             except Exception as e:
#                 logger.exception("Failed to post void credit note to IRD for hotel bill %s",
#                                  entry.bill_no)
#                 return Response(
#                     {"error": f"Failed to post credit note to IRD: {e}. Bill was NOT voided.",
#                      "code": "ird_post_failed"},
#                     status=status.HTTP_502_BAD_GATEWAY,
#                 )

#             logger.info(
#                 "IRD credit note response for hotel bill %s: code=%s message=%s raw=%r",
#                 entry.bill_no, ird_response.get('code'),
#                 ird_response.get('message'), ird_response.get('raw'),
#             )

#             if not ird_response.get("success"):
#                 code = ird_response.get("code")
#                 if code is None:
#                     detail = (f"Could not reach IRD: {ird_response.get('message')}. "
#                               f"Bill was NOT voided.")
#                     err_code = "ird_post_failed"
#                 else:
#                     detail = (f"IRD rejected the credit note: [{code}] "
#                               f"{ird_response.get('message')}. Bill was NOT voided.")
#                     err_code = "ird_rejected"
#                 return Response(
#                     {"error": detail, "code": err_code,
#                      "ird_code": code, "ird_message": ird_response.get("message")},
#                     status=status.HTTP_502_BAD_GATEWAY,
#                 )
#             ird_posted = True

#         # ---------- STEP 3: all DB writes atomically ----------
#         try:
#             with transaction.atomic():
#                 # lock + re-check: two simultaneous voids run one after the other
#                 locked = TblSalesEntry.objects.select_for_update().get(pk=entry.pk)
#                 if _already_voided(locked):
#                     return Response({"error": "This bill is already voided."},
#                                     status=status.HTTP_400_BAD_REQUEST)

#                 reversing_journal = create_reversing_journal_entry(
#                     locked.journal_entry_id, request.user.username
#                 )

#                 today = _date.today()
#                 TablReturnEntry.objects.create(
#                     bill_date=today,
#                     bill_no=locked.bill_no,
#                     customer_name=locked.customer_name,
#                     customer_pan=locked.customer_pan,
#                     amount=locked.amount,
#                     NoTaxSales=locked.NoTaxSales,
#                     ZeroTaxSales=locked.ZeroTaxSales,
#                     taxable_amount=locked.taxable_amount,
#                     tax_amount=locked.tax_amount,
#                     miti=_bs_str(today),
#                     ServicedItem=locked.ServicedItem,
#                     quantity=locked.quantity,
#                     reason=reason,
#                 )

#                 TblTaxEntry.objects.filter(
#                     bill_no=locked.bill_no, fiscal_year=locked.fiscal_year
#                 ).update(is_active="NO")

#         except Exception as e:
#             logger.exception("Failed to void hotel bill %s (%s) after IRD step",
#                              entry.bill_no, bill_date)
#             msg = f"Could not void bill {entry.bill_no}: {e}. Local changes were rolled back."
#             if ird_posted:
#                 msg += (" A credit note was already posted to IRD; "
#                         "contact support before retrying.")
#             return Response(
#                 {"error": msg,
#                  "code": "VOID_DB_FAILED_AFTER_IRD" if ird_posted else "VOID_DB_FAILED"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response(
#             {
#                 "bill_no": entry.bill_no,
#                 "bill_date": bill_date,
#                 "journal_entry_id": entry.journal_entry_id,
#                 "reversing_journal_id": reversing_journal.id,
#                 "voided": True,
#                 "warnings": warnings,
#             },
#             status=status.HTTP_200_OK,
#         )


# import logging
# from datetime import date as _date, datetime

# from django.db import IntegrityError, transaction
# from nepali_datetime import date as nepali_date
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from bill.models import TblSalesEntry, TblTaxEntry, TablReturnEntry, BillIndex
# from accounting.views import create_reversing_journal_entry
# from api.serializers.hotel.hotelbillvoid import HotelBillVoidSerializer
# # adjust these two imports to where they live in your project
# from bill.ird.postvoidbillintoird import post_credit_note_to_ird
# from bill.models import IrdCredentials

# logger = logging.getLogger(__name__)


# def _bs_str(d):
#     bs = nepali_date.from_datetime_date(d)
#     return f"{bs.year}.{bs.month:02d}.{bs.day:02d}"


# def _to_date(value):
#     """TblSalesEntry.bill_date may be a str, datetime or date."""
#     if isinstance(value, datetime):
#         return value.date()
#     if isinstance(value, _date):
#         return value
#     return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


# def _already_voided(entry):
#     """(fiscal_year, bill_no) is the stable identity of a bill."""
#     return TablReturnEntry.objects.filter(
#         bill_no=entry.bill_no,
#         fiscal_year=entry.fiscal_year,
#     ).exists()


# class HotelBillVoidAPIView(APIView):
#     """
#     POST /api/hotel-bills/void/
#     { "bill_no": "01-2-15", "bill_date": "2026-10-01",
#       "fiscal_year": "2083/84", "reason": "Wrong guest billed" }

#     1. Read-only checks (entry exists, has journal, not already voided, synced to IRD)
#     2. Post credit note to IRD (before any DB write)
#     3. Atomically: reverse journal, write TablReturnEntry, deactivate TblTaxEntry
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = HotelBillVoidSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         bill_no = serializer.validated_data['bill_no']
#         bill_date = serializer.validated_data['bill_date'].strftime('%Y-%m-%d')
#         fiscal_year = serializer.validated_data['fiscal_year']
#         reason = serializer.validated_data.get('reason') or "Voided Bill"

#         # ---------- STEP 1: read-only checks ----------
#         qs = TblSalesEntry.objects.filter(
#             bill_date=bill_date, bill_no=bill_no, fiscal_year=fiscal_year
#         )
#         entry = qs.filter(journal_entry__isnull=False).first()

#         if entry is None:
#             if qs.exists():
#                 return Response(
#                     {"error": f"Sales entry for bill {bill_no} has no linked journal entry, "
#                               f"so it cannot be reversed automatically."},
#                     status=status.HTTP_409_CONFLICT,
#                 )
#             return Response(
#                 {"error": f"No sales entry found for bill {bill_no} ({fiscal_year}) on {bill_date}."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         if _already_voided(entry):
#             return Response({"error": "This bill is already voided."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         tax_entry = TblTaxEntry.objects.filter(
#             bill_no=entry.bill_no, fiscal_year=entry.fiscal_year
#         ).first()

#         # IRD rejects a credit note for an invoice it never received
#         if tax_entry is not None and tax_entry.sync_with_ird != "Yes":
#             return Response(
#                 {
#                     "error": "The original bill has not been synced to IRD yet, so a credit note "
#                              "cannot be posted. Wait for the sync to complete and try again.",
#                     "code": "ORIGINAL_NOT_SYNCED",
#                 },
#                 status=status.HTTP_409_CONFLICT,
#             )

#         # ---------- STEP 2: credit note to IRD FIRST ----------
#         warnings = []
#         ird_posted = False
#         ird_creds = IrdCredentials.objects.first()

#         if not ird_creds:
#             logger.warning("No IRD credentials found, skipping IRD credit note for hotel bill %s",
#                            entry.bill_no)
#             warnings.append("No IRD credentials configured; skipped IRD posting.")
#         else:
#             Branch = BillIndex._meta.get_field('branch').related_model
#             branch = Branch.objects.first()
#             if not branch:
#                 return Response(
#                     {"error": "No branch configured; cannot build credit note number."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # same as the others void: credit note date = ORIGINAL bill date, in BS
#             bs_date_str = _bs_str(_to_date(entry.bill_date))

#             credit_note_payload = {
#                 "username": ird_creds.username,
#                 "password": ird_creds.password,
#                 "seller_pan": ird_creds.seller_pan,
#                 "buyer_pan": "0",
#                 "fiscal_year": entry.fiscal_year,
#                 "buyer_name": entry.customer_name,
#                 "ref_invoice_number": f"{entry.bill_no}",
#                 "credit_note_number": f"{branch.branch_code}-VOID-{entry.bill_no}",
#                 "credit_note_date": bs_date_str,
#                 "reason_for_return": reason if reason else "Voided Bill",
#                 "total_sales": float(entry.amount),
#                 "taxable_sales_vat": float(entry.taxable_amount),
#                 "vat": float(entry.tax_amount),
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
#                 ird_response = post_credit_note_to_ird(credit_note_payload)
#             except Exception as e:
#                 logger.exception("Failed to post void credit note to IRD for hotel bill %s",
#                                  entry.bill_no)
#                 return Response(
#                     {"error": f"Failed to post credit note to IRD: {e}. Bill was NOT voided.",
#                      "code": "ird_post_failed"},
#                     status=status.HTTP_502_BAD_GATEWAY,
#                 )

#             logger.info(
#                 "IRD credit note response for hotel bill %s: code=%s message=%s raw=%r",
#                 entry.bill_no, ird_response.get('code'),
#                 ird_response.get('message'), ird_response.get('raw'),
#             )

#             if not ird_response.get("success"):
#                 code = ird_response.get("code")
#                 if code is None:
#                     detail = (f"Could not reach IRD: {ird_response.get('message')}. "
#                               f"Bill was NOT voided.")
#                     err_code = "ird_post_failed"
#                 else:
#                     detail = (f"IRD rejected the credit note: [{code}] "
#                               f"{ird_response.get('message')}. Bill was NOT voided.")
#                     err_code = "ird_rejected"
#                 return Response(
#                     {"error": detail, "code": err_code,
#                      "ird_code": code, "ird_message": ird_response.get("message")},
#                     status=status.HTTP_502_BAD_GATEWAY,
#                 )
#             ird_posted = True

#         # ---------- STEP 3: all DB writes atomically ----------
#         try:
#             with transaction.atomic():
#                 # lock + re-check: two simultaneous voids run one after the other
#                 locked = TblSalesEntry.objects.select_for_update().get(pk=entry.pk)
#                 if _already_voided(locked):
#                     return Response({"error": "This bill is already voided."},
#                                     status=status.HTTP_400_BAD_REQUEST)

#                 reversing_journal = create_reversing_journal_entry(
#                     locked.journal_entry_id, request.user.username
#                 )

#                 today = _date.today()
#                 TablReturnEntry.objects.create(
#                     bill_date=today,
#                     bill_no=locked.bill_no,
#                     customer_name=locked.customer_name,
#                     customer_pan=locked.customer_pan,
#                     amount=locked.amount,
#                     NoTaxSales=locked.NoTaxSales,
#                     ZeroTaxSales=locked.ZeroTaxSales,
#                     taxable_amount=locked.taxable_amount,
#                     tax_amount=locked.tax_amount,
#                     miti=_bs_str(today),
#                     ServicedItem=locked.ServicedItem,
#                     quantity=locked.quantity,
#                     reason=reason,
#                     fiscal_year=locked.fiscal_year,
#                 )

#                 TblTaxEntry.objects.filter(
#                     bill_no=locked.bill_no, fiscal_year=locked.fiscal_year
#                 ).update(is_active="NO")

#         except IntegrityError:
#             # the unique (fiscal_year, bill_no) on TablReturnEntry caught a concurrent void;
#             # the whole transaction, including the journal reversal, has rolled back
#             logger.warning("Concurrent void blocked by unique constraint for hotel bill %s",
#                            entry.bill_no)
#             return Response({"error": "This bill is already voided."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             logger.exception("Failed to void hotel bill %s (%s) after IRD step",
#                              entry.bill_no, bill_date)
#             msg = f"Could not void bill {entry.bill_no}: {e}. Local changes were rolled back."
#             if ird_posted:
#                 msg += (" A credit note was already posted to IRD; "
#                         "contact support before retrying.")
#             return Response(
#                 {"error": msg,
#                  "code": "VOID_DB_FAILED_AFTER_IRD" if ird_posted else "VOID_DB_FAILED"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response(
#             {
#                 "bill_no": entry.bill_no,
#                 "bill_date": bill_date,
#                 "fiscal_year": entry.fiscal_year,
#                 "journal_entry_id": entry.journal_entry_id,
#                 "reversing_journal_id": reversing_journal.id,
#                 "voided": True,
#                 "warnings": warnings,
#             },
#             status=status.HTTP_200_OK,
#         )


import logging
from datetime import date as _date, datetime

from django.db import IntegrityError, transaction
from nepali_datetime import date as nepali_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bill.models import TblSalesEntry, TblTaxEntry, TablReturnEntry, BillIndex
from accounting.views import create_reversing_journal_entry
from api.serializers.hotel.hotelbillvoid import HotelBillVoidSerializer
# adjust these two imports to where they live in your project
from bill.ird.postvoidbillintoird import post_credit_note_to_ird
from bill.models import IrdCredentials

logger = logging.getLogger(__name__)


def _bs_str(d):
    bs = nepali_date.from_datetime_date(d)
    return f"{bs.year}.{bs.month:02d}.{bs.day:02d}"


def _to_date(value):
    """TblSalesEntry.bill_date may be a str, datetime or date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, _date):
        return value
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def _already_voided(entry):
    """(fiscal_year, bill_no) is the stable identity of a bill."""
    return TablReturnEntry.objects.filter(
        bill_no=entry.bill_no,
        fiscal_year=entry.fiscal_year,
    ).exists()


class HotelBillVoidAPIView(APIView):
    """
    POST /api/hotelbillvoid/
    { "bill_no": "01-2-15", "bill_date": "2026-10-01",
      "fiscal_year": "2083/84", "reason": "Wrong guest billed" }

    1. Read-only checks (entry exists, has journal, not already voided, synced to IRD)
    2. Post credit note to IRD (before any DB write)
    3. Atomically: reverse journal, write TablReturnEntry, deactivate TblTaxEntry
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HotelBillVoidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bill_no = serializer.validated_data['bill_no']
        bill_date = serializer.validated_data['bill_date'].strftime('%Y-%m-%d')
        fiscal_year = serializer.validated_data['fiscal_year']
        reason = serializer.validated_data.get('reason') or "Voided Bill"

        # ---------- STEP 1: read-only checks ----------
        qs = TblSalesEntry.objects.filter(
            bill_date=bill_date, bill_no=bill_no, fiscal_year=fiscal_year
        )
        entry = qs.filter(journal_entry__isnull=False).first()

        if entry is None:
            if qs.exists():
                return Response(
                    {"error": f"Sales entry for bill {bill_no} has no linked journal entry, "
                              f"so it cannot be reversed automatically."},
                    status=status.HTTP_409_CONFLICT,
                )
            return Response(
                {"error": f"No sales entry found for bill {bill_no} ({fiscal_year}) on {bill_date}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if _already_voided(entry):
            return Response({"error": "This bill is already voided."},
                            status=status.HTTP_400_BAD_REQUEST)

        tax_entry = TblTaxEntry.objects.filter(
            bill_no=entry.bill_no, fiscal_year=entry.fiscal_year
        ).first()

        # IRD rejects a credit note for an invoice it never received
        if tax_entry is not None and tax_entry.sync_with_ird != "Yes":
            return Response(
                {
                    "error": "The original bill has not been synced to IRD yet, so a credit note "
                             "cannot be posted. Wait for the sync to complete and try again.",
                    "code": "ORIGINAL_NOT_SYNCED",
                },
                status=status.HTTP_409_CONFLICT,
            )

        # ---------- STEP 2: credit note to IRD FIRST ----------
        warnings = []
        ird_posted = False
        ird_info = {"posted": False, "skipped": True}   # default: IRD step skipped
        ird_creds = IrdCredentials.objects.first()

        if not ird_creds:
            logger.warning("No IRD credentials found, skipping IRD credit note for hotel bill %s",
                           entry.bill_no)
            warnings.append("No IRD credentials configured; skipped IRD posting.")
        else:
            Branch = BillIndex._meta.get_field('branch').related_model
            branch = Branch.objects.first()
            if not branch:
                return Response(
                    {"error": "No branch configured; cannot build credit note number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # same as the others void: credit note date = ORIGINAL bill date, in BS
            bs_date_str = _bs_str(_to_date(entry.bill_date))

            credit_note_payload = {
                "username": ird_creds.username,
                "password": ird_creds.password,
                "seller_pan": ird_creds.seller_pan,
                "buyer_pan": "0",
                "fiscal_year": entry.fiscal_year,
                "buyer_name": entry.customer_name,
                "ref_invoice_number": f"{entry.bill_no}",
                "credit_note_number": f"{branch.branch_code}-VOID-{entry.bill_no}",
                "credit_note_date": bs_date_str,
                "reason_for_return": reason if reason else "Voided Bill",
                "total_sales": float(entry.amount),
                "taxable_sales_vat": float(entry.taxable_amount),
                "vat": float(entry.tax_amount),
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

            try:
                ird_response = post_credit_note_to_ird(credit_note_payload)
            except Exception as e:
                logger.exception("Failed to post void credit note to IRD for hotel bill %s",
                                 entry.bill_no)
                return Response(
                    {"error": f"Failed to post credit note to IRD: {e}. Bill was NOT voided.",
                     "code": "ird_post_failed"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            logger.info(
                "IRD credit note response for hotel bill %s: code=%s message=%s raw=%r",
                entry.bill_no, ird_response.get('code'),
                ird_response.get('message'), ird_response.get('raw'),
            )

            if not ird_response.get("success"):
                code = ird_response.get("code")
                if code is None:
                    detail = (f"Could not reach IRD: {ird_response.get('message')}. "
                              f"Bill was NOT voided.")
                    err_code = "ird_post_failed"
                else:
                    detail = (f"IRD rejected the credit note: [{code}] "
                              f"{ird_response.get('message')}. Bill was NOT voided.")
                    err_code = "ird_rejected"
                return Response(
                    {"error": detail, "code": err_code,
                     "ird_code": code, "ird_message": ird_response.get("message")},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            ird_posted = True
            ird_info = {
                "posted": True,
                "skipped": False,
                "code": ird_response.get("code"),
                "message": ird_response.get("message"),
                "credit_note_number": credit_note_payload["credit_note_number"],
                "credit_note_date": credit_note_payload["credit_note_date"],
            }

        # ---------- STEP 3: all DB writes atomically ----------
        try:
            with transaction.atomic():
                # lock + re-check: two simultaneous voids run one after the other
                locked = TblSalesEntry.objects.select_for_update().get(pk=entry.pk)
                if _already_voided(locked):
                    return Response({"error": "This bill is already voided."},
                                    status=status.HTTP_400_BAD_REQUEST)

                reversing_journal = create_reversing_journal_entry(
                    locked.journal_entry_id, request.user.username
                )

                today = _date.today()
                TablReturnEntry.objects.create(
                    bill_date=today,
                    bill_no=locked.bill_no,
                    customer_name=locked.customer_name,
                    customer_pan=locked.customer_pan,
                    amount=locked.amount,
                    NoTaxSales=locked.NoTaxSales,
                    ZeroTaxSales=locked.ZeroTaxSales,
                    taxable_amount=locked.taxable_amount,
                    tax_amount=locked.tax_amount,
                    miti=_bs_str(today),
                    ServicedItem=locked.ServicedItem,
                    quantity=locked.quantity,
                    reason=reason,
                    fiscal_year=locked.fiscal_year,
                )

                TblTaxEntry.objects.filter(
                    bill_no=locked.bill_no, fiscal_year=locked.fiscal_year
                ).update(is_active="NO")

        except IntegrityError:
            # unique (fiscal_year, bill_no) on TablReturnEntry caught a concurrent void;
            # the whole transaction, including the journal reversal, has rolled back
            logger.warning("Concurrent void blocked by unique constraint for hotel bill %s",
                           entry.bill_no)
            return Response({"error": "This bill is already voided."},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Failed to void hotel bill %s (%s) after IRD step",
                             entry.bill_no, bill_date)
            msg = f"Could not void bill {entry.bill_no}: {e}. Local changes were rolled back."
            if ird_posted:
                msg += (" A credit note was already posted to IRD; "
                        "contact support before retrying.")
            return Response(
                {"error": msg,
                 "code": "VOID_DB_FAILED_AFTER_IRD" if ird_posted else "VOID_DB_FAILED",
                 "ird": ird_info},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "bill_no": entry.bill_no,
                "bill_date": bill_date,
                "fiscal_year": entry.fiscal_year,
                "journal_entry_id": entry.journal_entry_id,
                "reversing_journal_id": reversing_journal.id,
                "voided": True,
                "ird": ird_info,
                "warnings": warnings,
            },
            status=status.HTTP_200_OK,
        )