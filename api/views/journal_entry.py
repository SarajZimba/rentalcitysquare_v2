from accounting.models import AccountLedger, AccountSubLedger, TblJournalEntry, TblCrJournalEntry, TblDrJournalEntry, TrackBill, AccountSubLedgerTracking
from django.shortcuts import render
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers.journal_entry import JournalEntrySerializer  # Import your serializer
from datetime import date, datetime

from accounting.utils import update_cumulative_ledger_journal, create_cumulative_ledger_journal, create_cumulative_ledger_journal_operationaldate
from accounting.utils import change_date_to_datetime
from accounting.operational_date_utils import parse_frontend_datetime, get_operational_date, get_operational_date_from_datetime

# class JournalEntryAPIView(APIView):

#     def post(self, request):
#         # entry_date = date.today()
#         # entry_datetime = datetime.now()


#         data_list = request.data  # Assuming you receive a list of JSON objects
        
#         print(f"non-credit-data {data_list}")
#         response_data = []
                


#         for raw_item in data_list:
#             serializer = JournalEntrySerializer(data=raw_item)

#             if serializer.is_valid():
#                 data = serializer.validated_data

#                 print(data)

#                 posted_datetime = data['datetime'] 

#                 posted_time = data['billPrintTime']

#                 # # 1️⃣ Build datetime from frontend
#                 # posted_datetime_frontend = parse_frontend_datetime(
#                 #     posted_datetime,
#                 #     posted_time
#                 # )

#                 # # 2️⃣ Calculate operational date
#                 # operational_date = get_operational_date_from_datetime(
#                 #     posted_datetime_frontend
#                 # )

#                 # operational_datetime = change_date_to_datetime(operational_date)

#                 if posted_time != '':

#                     # 1️⃣ Build datetime from frontend
#                     posted_datetime_frontend = parse_frontend_datetime(
#                         posted_datetime,
#                         posted_time
#                     )

#                     # 2️⃣ Calculate operational date
#                     operational_date = get_operational_date_from_datetime(
#                         posted_datetime_frontend
#                     )

#                     operational_datetime = change_date_to_datetime(operational_date)
#                 else:

#                     operational_datetime = change_date_to_datetime(posted_datetime)
#                     operational_date = operational_datetime.date() if operational_datetime else None

#                 # Use your utility function
#                 entry_datetime = change_date_to_datetime(posted_datetime)

#                 # For TblJournalEntry which only needs a date
#                 entry_date = entry_datetime.date() if entry_datetime else None
#                 debit_ledgers = data['debit_ledgers']
#                 debit_particulars = data['debit_particulars']
#                 debit_amounts = data['debit_amounts']


#                 credit_ledgers = data['credit_ledgers']
#                 credit_particulars = data['credit_particulars']
#                 credit_amounts = data['credit_amounts']

#                 posted_datetime = data['datetime']
#                 id = data['bill_id']
#                 username = data['user']
                
#                 outlet_name = data['outlet_name']

#                 # try:
#                 #     outlet_subledger = check_outlet_subledger(outlet_name)
#                 # except Exception as e:
#                 #     return Response({'message': 'Error occured while creating the outlet subledger'}, 400)
#                 try:
#                     outlet_subledger = get_hotel_sales_subledger()
#                 except Exception as e:
#                     return Response({'message': 'Error occured while creating the outlet subledger'}, 400)

#                 try:
#                     parsed_debitamt = [Decimal(i) for i in debit_amounts]
#                     parsed_creditamt = [Decimal(i) for i in credit_amounts]
#                 except Exception:
#                     response_data.append({'message': 'Please Enter a valid amount'})
#                     continue  

#                 debit_sum, credit_sum = sum(parsed_debitamt), sum(parsed_creditamt)

#                 if len(credit_ledgers) != len(credit_particulars):
#                     response_data.append({'message': 'Number of Credit Ledgers and Credit Particulars must be the same'})
#                     continue 

#                 # Validate that debit and credit totals are equal
#                 if debit_sum != credit_sum:
#                     response_data.append({'message': 'Debit Total and Credit Total must be equal'})
#                     continue  # Skip this entry and move to the next one

#                 # Validate debit and credit ledgers
#                 for dr in debit_ledgers:
#                     if dr.startswith('-'):
#                         response_data.append({'message': 'Ledger must be selected'})
#                         continue  # Skip this entry and move to the next one

#                     if not AccountLedger.objects.filter(pk=dr).exists():
#                         response_data.append({'message': 'There is no debit_ledger of that id in the database'})
#                         continue  # Skip this entry and move to the next one

#                 for cr in credit_ledgers:
#                     if cr.startswith('-'):
#                         response_data.append({'message': 'Ledger must be selected'})
#                         continue  # Skip this entry and move to the next one

#                     if not AccountLedger.objects.filter(pk=cr).exists():
#                         response_data.append({'message': 'There is no credit_ledger of that id in the database'})
#                         continue  # Skip this entry and move to the next one



#                 if TrackBill.objects.filter(datetime=posted_datetime, bill=id).exists():
#                     response_data.append({'message': 'Entry with the same datetime and id already exists'})
#                     continue
                
#                 else:
#                     TrackBill.objects.create(datetime=posted_datetime, bill=id)
#                 if id != '':
#                     if TrackBill.objects.filter(datetime=posted_datetime, bill=id).exists():
#                         response_data.append({'message': 'Entry with the same datetime and id already exists'})
#                         print('Entry with the same datetime and id already exists')
#                         continue
                    
#                     else:
#                         TrackBill.objects.create(datetime=posted_datetime, bill=id)

#                 credit_to_debit_mapping = {}
                
#                 # Create a journal entry
#                 journal_entry = TblJournalEntry.objects.create(employee_name=username, journal_total=debit_sum, entry_date=entry_date)

#                 # Process credit entries
#                 for i in range(len(credit_ledgers)):
#                     credit_ledger_id = int(credit_ledgers[i])
#                     credit_ledger = AccountLedger.objects.get(pk=credit_ledger_id)
#                     credit_particular = credit_particulars[i]
#                     credit_amount = parsed_creditamt[i]
#                     credit_ledger_type = credit_ledger.account_chart.account_type
#                     # TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry, particulars=credit_particular, credit_amount=credit_amount)
#                     if credit_ledger.ledger_name == "Sales":                    
#                         TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry, particulars=credit_particular, credit_amount=credit_amount, sub_ledger=outlet_subledger)
#                     else:
#                         TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry, particulars=credit_particular, credit_amount=credit_amount) 

#                     # Update ledger and subledger totals
#                     if credit_ledger_type in ['Asset', 'Expense']:
#                         credit_ledger.total_value = credit_ledger.total_value - credit_amount
#                         credit_ledger.save()
#                         create_cumulative_ledger_journal_operationaldate(credit_ledger, journal_entry, entry_datetime, operational_datetime)

#                     elif credit_ledger_type in ['Liability', 'Revenue', 'Equity']:
#                         credit_ledger.total_value = credit_ledger.total_value + credit_amount
#                         credit_ledger.save()
#                         create_cumulative_ledger_journal_operationaldate(credit_ledger, journal_entry, entry_datetime, operational_datetime)

#                         if credit_ledger.ledger_name == "Sales":
#                             prev_value = outlet_subledger.total_value
#                             subledgertracking = AccountSubLedgerTracking.objects.create(subledger = outlet_subledger, prev_amount= prev_value, journal=journal_entry)

#                             outlet_subledger.total_value = outlet_subledger.total_value + credit_amount
#                             outlet_subledger.save()
#                             subledgertracking.new_amount=outlet_subledger.total_value
#                             subledgertracking.value_changed = outlet_subledger.total_value - prev_value
#                             subledgertracking.save()

#                 # Process debit entries
#                 for i in range(len(debit_ledgers)):
#                     debit_ledger_id = int(debit_ledgers[i])
#                     debit_ledger = AccountLedger.objects.get(pk=debit_ledger_id)
#                     debit_particular = debit_particulars[i]
#                     debit_amount = parsed_debitamt[i]
#                     debit_ledger_type = debit_ledger.account_chart.account_type
#                     TblDrJournalEntry.objects.create(ledger=debit_ledger, journal_entry=journal_entry, particulars=debit_particular, debit_amount=debit_amount, paidfrom_ledger=credit_to_debit_mapping.get(credit_ledger))

#                     # Update ledger and subledger totals
#                     if debit_ledger_type in ['Asset', 'Expense']:
#                         debit_ledger.total_value = debit_ledger.total_value + debit_amount
#                         debit_ledger.save()
#                         create_cumulative_ledger_journal_operationaldate(debit_ledger, journal_entry, entry_datetime, operational_datetime)

#                     elif debit_ledger_type in ['Liability', 'Revenue', 'Equity']:
#                         debit_ledger.total_value = debit_ledger.total_value - debit_amount
#                         debit_ledger.save()
#                         create_cumulative_ledger_journal_operationaldate(debit_ledger, journal_entry, entry_datetime, operational_datetime)


#                 result = {'message': 'Journal entry created successfully'}
#                 try:
#                     result['sales_bill_no'] = create_hotel_sales_entry(raw_item, entry_date, journal_entry).bill_no
#                 except Exception as e:
#                     result['sales_entry_error'] = str(e)
#                 response_data.append(result)

#             else:
#                 response_data.append({'error': serializer.errors})
#         return Response(response_data, status=status.HTTP_201_CREATED)


class JournalError(Exception):
    """Raised to abort the whole request (rolled back) with a specific HTTP status."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class JournalPostMixin:
    def post(self, request):
        data_list = request.data
        if not isinstance(data_list, list) or not data_list:
            return Response({"error": "Expected a non-empty list of journal entries."}, status=400)

        try:
            with transaction.atomic():
                response_data = [self._create_entry(item) for item in data_list]
        except JournalError as e:
            return Response({"error": e.message}, status=e.status_code)
        except IntegrityError:
            # lost a race with an identical request; the transaction has already rolled back
            try:
                response_data = [find_existing_hotel_posting(item) for item in data_list]
            except JournalError as e:
                return Response({"error": e.message}, status=e.status_code)
            if not all(response_data):
                logger.exception("Journal entry integrity error")
                return Response({"error": "Integrity error while creating journal entry"}, status=409)
        except Exception as e:
            logger.exception("Journal entry creation failed")
            return Response({"error": str(e)}, status=500)

        all_dupes = all(r.get("already_posted") for r in response_data)
        return Response(response_data, status=200 if all_dupes else 201)


class JournalEntryAPIView(JournalPostMixin, APIView):

    def _create_entry(self, raw_item):
        serializer = JournalEntrySerializer(data=raw_item)
        if not serializer.is_valid():
            raise JournalError(f"Invalid journal data: {serializer.errors}", 400)

        data = serializer.validated_data
        print(data)

        posted_datetime = data['datetime']
        posted_time = data['billPrintTime']

        if posted_time != '':
            posted_datetime_frontend = parse_frontend_datetime(posted_datetime, posted_time)
            operational_date = get_operational_date_from_datetime(posted_datetime_frontend)
            operational_datetime = change_date_to_datetime(operational_date)
        else:
            operational_datetime = change_date_to_datetime(posted_datetime)
            operational_date = operational_datetime.date() if operational_datetime else None

        entry_datetime = change_date_to_datetime(posted_datetime)
        entry_date = entry_datetime.date() if entry_datetime else None
        existing = find_existing_hotel_posting(raw_item, entry_date)
        if existing:
            return existing
        debit_ledgers = data['debit_ledgers']
        debit_particulars = data['debit_particulars']
        debit_amounts = data['debit_amounts']

        credit_ledgers = data['credit_ledgers']
        credit_particulars = data['credit_particulars']
        credit_amounts = data['credit_amounts']

        bill_ref = data['bill_id']
        username = data['user']

        # -------- VALIDATION (every failure aborts and rolls back) --------
        try:
            parsed_debitamt = [Decimal(i) for i in debit_amounts]
            parsed_creditamt = [Decimal(i) for i in credit_amounts]
        except Exception:
            raise JournalError('Please Enter a valid amount', 400)

        if not (len(debit_ledgers) == len(debit_particulars) == len(parsed_debitamt)):
            raise JournalError('Number of Debit Ledgers, Particulars and Amounts must be the same', 400)

        if not (len(credit_ledgers) == len(credit_particulars) == len(parsed_creditamt)):
            raise JournalError('Number of Credit Ledgers, Particulars and Amounts must be the same', 400)

        debit_sum, credit_sum = sum(parsed_debitamt), sum(parsed_creditamt)
        if debit_sum != credit_sum:
            raise JournalError('Debit Total and Credit Total must be equal', 400)

        for side, ledger_ids in (('debit', debit_ledgers), ('credit', credit_ledgers)):
            for ledger_id in ledger_ids:
                if str(ledger_id).startswith('-'):
                    raise JournalError('Ledger must be selected', 400)
                if not AccountLedger.objects.filter(pk=ledger_id).exists():
                    raise JournalError(f'There is no {side}_ledger of that id in the database', 400)

        try:
            outlet_subledger = get_hotel_sales_subledger()
        except Exception as e:
            raise JournalError(f'Could not get the Hotel subledger: {e}', 500)

        # -------- DUPLICATE CHECK (single block) --------
        if bill_ref != '':
            if TrackBill.objects.filter(datetime=posted_datetime, bill=bill_ref).exists():
                raise JournalError('Entry with the same datetime and id already exists', 409)
            TrackBill.objects.create(datetime=posted_datetime, bill=bill_ref)

        credit_to_debit_mapping = {}

        # -------- JOURNAL ENTRY --------
        journal_entry = TblJournalEntry.objects.create(
            employee_name=username,
            journal_total=debit_sum,
            entry_date=entry_date
        )

        # Process credit entries
        for i in range(len(credit_ledgers)):
            credit_ledger_id = int(credit_ledgers[i])
            credit_ledger = AccountLedger.objects.get(pk=credit_ledger_id)
            credit_particular = credit_particulars[i]
            credit_amount = parsed_creditamt[i]
            credit_ledger_type = credit_ledger.account_chart.account_type

            if credit_ledger.ledger_name == "Sales":
                TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry, particulars=credit_particular, credit_amount=credit_amount, sub_ledger=outlet_subledger)
            else:
                TblCrJournalEntry.objects.create(ledger=credit_ledger, journal_entry=journal_entry, particulars=credit_particular, credit_amount=credit_amount)

            if credit_ledger_type in ['Asset', 'Expense']:
                credit_ledger.total_value = credit_ledger.total_value - credit_amount
                credit_ledger.save()
                create_cumulative_ledger_journal_operationaldate(credit_ledger, journal_entry, entry_datetime, operational_datetime)

            elif credit_ledger_type in ['Liability', 'Revenue', 'Equity']:
                credit_ledger.total_value = credit_ledger.total_value + credit_amount
                credit_ledger.save()
                create_cumulative_ledger_journal_operationaldate(credit_ledger, journal_entry, entry_datetime, operational_datetime)

                if credit_ledger.ledger_name == "Sales":
                    prev_value = outlet_subledger.total_value
                    subledgertracking = AccountSubLedgerTracking.objects.create(subledger=outlet_subledger, prev_amount=prev_value, journal=journal_entry)

                    outlet_subledger.total_value = outlet_subledger.total_value + credit_amount
                    outlet_subledger.save()
                    subledgertracking.new_amount = outlet_subledger.total_value
                    subledgertracking.value_changed = outlet_subledger.total_value - prev_value
                    subledgertracking.save()

        # Process debit entries
        for i in range(len(debit_ledgers)):
            debit_ledger_id = int(debit_ledgers[i])
            debit_ledger = AccountLedger.objects.get(pk=debit_ledger_id)
            debit_particular = debit_particulars[i]
            debit_amount = parsed_debitamt[i]
            debit_ledger_type = debit_ledger.account_chart.account_type
            TblDrJournalEntry.objects.create(ledger=debit_ledger, journal_entry=journal_entry, particulars=debit_particular, debit_amount=debit_amount, paidfrom_ledger=credit_to_debit_mapping.get(credit_ledger))

            if debit_ledger_type in ['Asset', 'Expense']:
                debit_ledger.total_value = debit_ledger.total_value + debit_amount
                debit_ledger.save()
                create_cumulative_ledger_journal_operationaldate(debit_ledger, journal_entry, entry_datetime, operational_datetime)

            elif debit_ledger_type in ['Liability', 'Revenue', 'Equity']:
                debit_ledger.total_value = debit_ledger.total_value - debit_amount
                debit_ledger.save()
                create_cumulative_ledger_journal_operationaldate(debit_ledger, journal_entry, entry_datetime, operational_datetime)

        # -------- SALES ENTRY (any failure rolls back the whole journal) --------
        sales_entry = create_hotel_sales_entry(raw_item, entry_date, journal_entry)

        return {
            'message': 'Journal entry created successfully',
            'sales_bill_no': sales_entry.bill_no,
        }
        
        
# This function checks if the subledger for that outlet_name exists or not and if it does not exist then it creates it.
def check_outlet_subledger(outlet_name):

    sales_ledger = AccountLedger.objects.get(ledger_name='Sales')
    outlet_subledger_exists = AccountSubLedger.objects.filter(ledger=sales_ledger, sub_ledger_name=outlet_name).exists()

    if outlet_subledger_exists:
        outlet_subledger = AccountSubLedger.objects.get(ledger=sales_ledger, sub_ledger_name=outlet_name)
    else:
        outlet_subledger = AccountSubLedger.objects.create(ledger=sales_ledger, sub_ledger_name=outlet_name)

    return outlet_subledger


from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from bill.models import TblSalesEntry, TblTaxEntry, BillIndex

HOTEL_SUBLEDGER_NAME = "Hotel"
HOTEL_BILL_TERMINAL = "2"


def get_hotel_sales_subledger():
    """Get-or-create the 'Hotel' subledger under Sales (same pattern as 'Rental')."""
    sales_ledger = AccountLedger.objects.get(ledger_name='Sales')
    subledger, _ = AccountSubLedger.objects.get_or_create(
        ledger=sales_ledger,
        sub_ledger_name=HOTEL_SUBLEDGER_NAME,
        defaults={'is_editable': True},
    )
    return subledger


def next_terminal_bill_no(terminal=HOTEL_BILL_TERMINAL):
    """
    Return the next bill number for the terminal and advance the counter.
    Must run inside transaction.atomic() so the row lock holds.
    bill_index is treated as the NEXT number to issue.
    """
    Branch = BillIndex._meta.get_field('branch').related_model
    branch = Branch.objects.first()          # only one branch for now

    index = (BillIndex.objects.select_for_update()
             .filter(terminal=terminal, branch=branch).first())
    if index is None:
        index = BillIndex.objects.create(terminal=terminal, branch=branch, bill_index=1)

    number = index.bill_index
    index.bill_index = number + 1
    index.save()
    bill_number = str(branch.branch_code) + "-" + str(terminal) + "-" + str(number)
    return bill_number


def advance_bill_index(bill_no, terminal=HOTEL_BILL_TERMINAL):
    """Move the counter past a number that was just used. Runs inside the journal transaction."""
    try:
        number = int(str(bill_no).rsplit("-", 1)[-1])
    except ValueError:
        return
    Branch = BillIndex._meta.get_field('branch').related_model
    branch = Branch.objects.first()
    index = (BillIndex.objects.select_for_update()
             .filter(terminal=terminal, branch=branch).first())
    if index is None:
        BillIndex.objects.create(terminal=terminal, branch=branch, bill_index=number + 1)
    elif index.bill_index <= number:
        index.bill_index = number + 1
        index.save()

def _money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

from nepali_datetime import date as nepali_date
def create_hotel_sales_entry(raw, entry_date, journal_entry=None):
    total = _money(raw.get('total_amount'))
    vat = _money(raw.get('vat_amount'))
    taxable = (total - vat) if vat > 0 else Decimal('0.00')

    miti = raw.get('miti')
    if not miti and entry_date:
        bs = nepali_date.from_datetime_date(entry_date)
        miti = f"{bs.year}.{bs.month:02d}.{bs.day:02d}"

    with transaction.atomic():
        provided = raw.get('sales_bill_no')
        bill_no = provided if provided not in (None, '') else next_terminal_bill_no()

        entry = TblSalesEntry(
            bill_no=str(bill_no),
            bill_date=entry_date.strftime('%Y-%m-%d') if entry_date else None,
            customer_name=raw.get('customer_name'),
            customer_pan=raw.get('customer_pan'),
            amount=total,
            NoTaxSales=0,
            ZeroTaxSales=0,
            taxable_amount=taxable,
            tax_amount=vat,
            miti=miti,
            quantity=1,
            journal_entry=journal_entry,
            fiscal_year=raw.get('fiscal_year'),
            ird_synced=False,
        )
        if vat == 0:
            entry.exemptedSales = str(total)
        entry.save()

        tax_entry = TblTaxEntry(
            fiscal_year=raw.get('fiscal_year'),
            bill_no=str(bill_no),
            customer_name=raw.get('customer_name'),
            customer_pan=raw.get('customer_pan'),
            bill_date=entry_date.strftime('%Y-%m-%d') if entry_date else None,
            amount=total,
            taxable_amount=taxable,
            tax_amount=vat,
            is_printed="Yes",
            printed_time=datetime.now().strftime("%I:%M %p"),
            entered_by=raw.get('user'),
            printed_by=raw.get('user'),
            is_realtime="No",            # the sync flips this to "Yes" on a first-attempt success
            sync_with_ird="No",          # flipped to "Yes" only after a confirmed IRD success
            payment_method=raw.get('payment_mode', None),
            vat_refund_amount=0.0,
            transaction_id="-",
        )
        if vat == 0:
            tax_entry.exemptedSales = str(total)
        tax_entry.save()
        if provided not in (None, ''):
            advance_bill_index(bill_no)
        # runs only after the whole request commits, so IRD never sees a rolled-back bill
        schedule_hotel_ird_sync(entry.pk)

    return entry

import threading
from django.db import connection

import logging

logger = logging.getLogger(__name__)
def _run_hotel_ird_sync(entry_id):
    from bill.utils import attempt_hotel_ird_sync, sync_pending_hotel_ird
    try:
        synced = attempt_hotel_ird_sync(entry_id)
        if synced is True:
            # IRD is reachable, so clear a few older failures too
            sync_pending_hotel_ird(exclude_ids=[entry_id])
    except Exception:
        logger.exception(f"Hotel IRD sync crashed for sales entry {entry_id}")
    finally:
        connection.close()      # this thread's own DB connection


def schedule_hotel_ird_sync(entry_id):
    transaction.on_commit(
        lambda: threading.Thread(target=_run_hotel_ird_sync, args=(entry_id,), daemon=True).start()
    )

from django.db import IntegrityError

def find_existing_hotel_posting(raw_item, entry_date=None):
    """Return the 'already posted' result if this bill was already journaled, else None.
    Raises JournalError(409) if the number is used by a *different* bill."""
    bill_no = str(raw_item.get("sales_bill_no") or "").strip()
    fiscal_year = raw_item.get("fiscal_year")
    if not bill_no or not fiscal_year:
        return None

    existing = TblSalesEntry.objects.filter(fiscal_year=fiscal_year, bill_no=bill_no).first()
    if existing is None:
        return None

    same_total = _money(raw_item.get("total_amount")) == existing.amount
    same_date = (
        entry_date is None
        or str(existing.bill_date) == entry_date.strftime("%Y-%m-%d")
    )
    if not (same_total and same_date):
        raise JournalError(
            f"Bill number {bill_no} ({fiscal_year}) is already used by a different bill", 409
        )

    return {
        "message": "Journal entry already posted",
        "sales_bill_no": existing.bill_no,
        "already_posted": True,
    }
    
