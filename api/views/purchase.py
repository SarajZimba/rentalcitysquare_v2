# import decimal
# import json
# from datetime import datetime

# from django.db import transaction, IntegrityError
# from django.shortcuts import get_object_or_404
# from django.db.models import Q

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from purchase.models import Purchase, ProductPurchase, TblpurchaseEntry
# from purchase.utils import update_cumulative_ledger_purchase, create_cumulative_ledger_purchase
# from accounting.models import (
#     AccountLedger, AccountSubLedger, AccountSubLedgerTracking,
#     AccountChart, TblJournalEntry, TblDrJournalEntry, TblCrJournalEntry,
# )
# from product.models import Product, ProductCategory
# from purchase.models import Vendor
# from product.models import BranchStock, RequisitionBranchStock
# # adjust the import paths above to match your actual app layout

# # from .permissions import IsAdminMixin  # or whatever perm class you use for is_admin check


# def change_date_to_datetime(entry_date):
#     """same helper you already use elsewhere"""
#     if isinstance(entry_date, datetime):
#         return entry_date
#     return datetime.strptime(entry_date, "%Y-%m-%d")


# class PurchaseCreateAPI(APIView):
#     """
#     POST body shape (JSON):

#     {
#       "bill_no": "PB-001",
#       "bill_date": "2026-07-14",
#       "pp_no": "PP-001",
#       "vendor_id": 3,
#       "sub_total": "1000",
#       "discount_percentage": "0",
#       "discount_amount": "0",
#       "taxable_amount": "1000",
#       "non_taxable_amount": "0",
#       "tax_amount": "130",
#       "grand_total": "1130",
#       "amount_in_words": "One thousand one hundred thirty only",
#       "payment_mode": "credit",           # credit | mobile payment | credit card | complimentary | Bank:<subledger_name> | cash(default)
#       "debit_account": 5,                  # default ledger, kept for parity with old view (currently unused downstream)

#       "items": [                           # existing products
#         {"product_id": 12, "ledger_id": 5, "quantity": 2, "rate": 100, "total": 200}
#       ],

#       "new_items": [                       # products that need to be created on the fly
#         {
#           "key": "cold-drink-500ml",
#           "category": "beverages",
#           "ledger_id": 5,
#           "is_taxable": true,
#           "quantity": 3,
#           "rate": 50
#         }
#       ]
#     }
#     """
#     # permission_classes = [IsAdminMixin]  # swap for IsAuthenticated / your own perm class

#     # ---------- helpers (ported almost 1:1 from the CBV) ----------

#     def create_subledgers(self, product, item_total, ledger_id):
#         debit_account = get_object_or_404(AccountLedger, pk=int(ledger_id))
#         subledgername = f'{product.title} ({product.category.title}) - Purchase'
#         try:
#             sub = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=debit_account)
#             prev_value = sub.total_value
#             tracking = AccountSubLedgerTracking.objects.create(subledger=sub, prev_amount=prev_value)
#             sub.total_value += decimal.Decimal(item_total)
#             sub.save()
#             tracking.new_amount = sub.total_value
#             tracking.value_changed = sub.total_value - prev_value
#             tracking.save()
#         except AccountSubLedger.DoesNotExist:
#             AccountSubLedger.objects.create(
#                 sub_ledger_name=subledgername, ledger=debit_account, total_value=item_total
#             )
#             # note: tracking row for the create-path wasn't saved in the original either,
#             # keeping behaviour identical - fix here if that was a bug, not a feature.

#     def create_accounting_single_ledger(self, ledger_totals, payment_mode, username,
#                                          tax_amount, vendor, entry_date, purchase_object):
#         sub_total = sum(decimal.Decimal(str(total)) for total in ledger_totals.values())
#         total_amount = sub_total + tax_amount

#         cash_ledger = get_object_or_404(AccountLedger, ledger_name='Cash-In-Hand')
#         vat_receivable = get_object_or_404(AccountLedger, ledger_name='VAT Receivable')

#         journal_entry = TblJournalEntry.objects.create(
#             employee_name=username,
#             journal_total=total_amount,
#             entry_date=entry_date,
#             purchase_journal=purchase_object,
#         )

#         entry_datetime = change_date_to_datetime(entry_date) if entry_date else datetime.now()

#         for ledger_id, amount in ledger_totals.items():
#             ledger = get_object_or_404(AccountLedger, pk=int(ledger_id))
#             TblDrJournalEntry.objects.create(
#                 journal_entry=journal_entry,
#                 particulars=f"Automatic: {ledger.ledger_name} A/c Dr.",
#                 debit_amount=decimal.Decimal(str(amount)),
#                 ledger=ledger,
#             )
#             ledger.total_value += decimal.Decimal(str(amount))
#             ledger.save()
#             update_cumulative_ledger_purchase(ledger, entry_datetime, journal_entry)

#         if tax_amount > 0:
#             TblDrJournalEntry.objects.create(
#                 journal_entry=journal_entry,
#                 particulars="Automatic: VAT Receivable A/c Dr.",
#                 debit_amount=tax_amount,
#                 ledger=vat_receivable,
#             )
#             vat_receivable.total_value += tax_amount
#             vat_receivable.save()
#             update_cumulative_ledger_purchase(vat_receivable, entry_datetime, journal_entry)

#         mode = payment_mode.lower().strip()

#         if mode == "credit":
#             try:
#                 vendor_ledger = AccountLedger.objects.get(ledger_name=vendor)
#                 vendor_ledger.total_value += total_amount
#                 vendor_ledger.save()
#                 update_cumulative_ledger_purchase(vendor_ledger, entry_datetime, journal_entry)
#             except AccountLedger.DoesNotExist:
#                 chart = AccountChart.objects.get(group__iexact='Sundry Creditors')
#                 vendor_ledger = AccountLedger.objects.create(
#                     ledger_name=vendor, total_value=total_amount, is_editable=True, account_chart=chart
#                 )
#                 create_cumulative_ledger_purchase(vendor_ledger, entry_datetime, journal_entry)

#             TblCrJournalEntry.objects.create(
#                 journal_entry=journal_entry,
#                 particulars=f"Automatic: To {vendor_ledger.ledger_name} A/c",
#                 credit_amount=total_amount,
#                 ledger=vendor_ledger,
#             )

#         elif mode in ("mobile payment", "credit card", "complimentary"):
#             ledger_name = {
#                 "mobile payment": "Mobile Payments",
#                 "credit card": "Card Transactions",
#                 "complimentary": "Complimentary Expenses",
#             }[mode]
#             ledger = get_object_or_404(AccountLedger, ledger_name=ledger_name)
#             TblCrJournalEntry.objects.create(
#                 journal_entry=journal_entry,
#                 particulars=f"Automatic: To {ledger.ledger_name} A/c",
#                 credit_amount=total_amount,
#                 ledger=ledger,
#             )
#             ledger.total_value -= total_amount
#             ledger.save()
#             update_cumulative_ledger_purchase(ledger, entry_datetime, journal_entry)

#         elif payment_mode.startswith("Bank:"):
#             subledger_name = payment_mode.replace("Bank:", "").strip()
#             bank_account_ledger = get_object_or_404(AccountLedger, ledger_name='Bank Accounts')
#             try:
#                 subledger = AccountSubLedger.objects.get(
#                     sub_ledger_name=subledger_name, ledger=bank_account_ledger
#                 )
#             except AccountSubLedger.DoesNotExist:
#                 raise ValueError(f"Subledger '{subledger_name}' not found under 'Bank Accounts'")

#             TblCrJournalEntry.objects.create(
#                 journal_entry=journal_entry,
#                 particulars=f"Automatic: To {bank_account_ledger.ledger_name} A/c",
#                 credit_amount=total_amount,
#                 ledger=bank_account_ledger,
#             )
#             bank_account_ledger.total_value -= total_amount
#             bank_account_ledger.save()
#             update_cumulative_ledger_purchase(bank_account_ledger, entry_datetime, journal_entry)

#             prev_value = subledger.total_value
#             subledger_tracking = AccountSubLedgerTracking.objects.create(
#                 subledger=subledger, prev_amount=prev_value, journal=journal_entry
#             )
#             subledger.total_value -= total_amount
#             subledger.save()
#             subledger_tracking.new_amount = subledger.total_value
#             subledger_tracking.value_changed = subledger.total_value - prev_value
#             subledger_tracking.save()

#         else:
#             TblCrJournalEntry.objects.create(
#                 journal_entry=journal_entry,
#                 particulars=f"Automatic: To {cash_ledger.ledger_name} A/c",
#                 credit_amount=total_amount,
#                 ledger=cash_ledger,
#             )
#             cash_ledger.total_value -= total_amount
#             cash_ledger.save()
#             update_cumulative_ledger_purchase(cash_ledger, entry_datetime, journal_entry)

#     # ---------- validation ----------

#     def validate_payload(self, data):
#         required = [
#             'bill_no', 'bill_date', 'sub_total', 'tax_amount',
#             'grand_total', 'payment_mode',
#         ]
#         missing = [f for f in required if data.get(f) in (None, '')]
#         if missing:
#             return f"Missing required fields: {', '.join(missing)}"

#         items = data.get('items', [])
#         new_items = data.get('new_items', [])
#         if not items and not new_items:
#             return "At least one item (existing or new) is required."

#         for i, item in enumerate(items):
#             for key in ('product_title', 'quantity', 'rate', 'total'):
#                 if item.get(key) in (None, ''):
#                     return f"items[{i}] missing '{key}'"

#         for i, item in enumerate(new_items):
#             for key in ('key', 'category', 'ledger_id', 'quantity', 'rate'):
#                 if item.get(key) in (None, ''):
#                     return f"new_items[{i}] missing '{key}'"

#         return None

#     # ---------- main entrypoint ----------

#     @transaction.atomic
#     def post(self, request):
#         data = request.data
#         error = self.validate_payload(data)
#         if error:
#             return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             vendor = Vendor.objects.get(name='Aqua Minerals Nepal Pvt Ltd.')
#         except Vendor.DoesNotExist:
#             return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

#         print("We got the branch id as ", data.get("branch"))

#         branch_id = data.get("branch")

#         purchase_object = Purchase.objects.create(
#             bill_no=data.get('bill_no'),
#             vendor_id=vendor.id,
#             sub_total=data.get('sub_total'),
#             bill_date=data.get('bill_date'),
#             discount_percentage=data.get('discount_percentage', 0),
#             discount_amount=data.get('discount_amount', 0),
#             taxable_amount=data.get('taxable_amount', 0),
#             non_taxable_amount=data.get('non_taxable_amount', 0),
#             tax_amount=data.get('tax_amount', 0),
#             grand_total=data.get('grand_total'),
#             amount_in_words=data.get('amount_in_words', ''),
#             payment_mode=data.get('payment_mode'),
#         )

#         ledger_totals = {}
#         total_quantity = 0

#         # ---- existing products ----
#         for item in data.get('items', []):
#             try:
#                 product_title = item['product_title']
#                 quantity = float(item['quantity'])
#                 rate = float(item['rate'])
#                 item_total = quantity * rate
#                 total = float(item['total'])

#                 prod = Product.objects.get(title=product_title)

#                 if prod.ledger:
#                     ledger_id = prod.ledger.id
#                 else:
#                     ledger_id = AccountLedger.objects.get(ledger_name = 'Inventory Purchases').id


#                 self.create_subledgers(prod, item_total, ledger_id)
#                 ProductPurchase.objects.create(
#                     product=prod, purchase=purchase_object,
#                     quantity=quantity, rate=rate, item_total=total,
#                 )
#                 total_quantity += quantity
#                 ledger_totals[ledger_id] = ledger_totals.get(ledger_id, 0) + total

#                 if branch_id:
#                     BranchStock.objects.create(branch_id=data.get("branch"), product_id=prod.id, quantity=quantity)
#                     RequisitionBranchStock.objects.create(branch_id=data.get("branch"), product_id=prod.id, quantity=quantity)

#             except (ValueError, KeyError, Product.DoesNotExist, AccountLedger.DoesNotExist):
#                 continue  # mirrors the silent-skip behaviour of the original view

#         # ---- new / on-the-fly products ----
#         for item in data.get('new_items', []):
#             key = item['key']
#             category_name = str(item.get('category', '')).lower().strip()

#             category = ProductCategory.objects.filter(title__iexact=category_name).first()
#             if not category:
#                 try:
#                     category = ProductCategory.objects.create(title=category_name)
#                 except IntegrityError:
#                     category = ProductCategory.objects.filter(title__iexact=category_name).first()

#             rate = float(item['rate'])
#             quantity = float(item['quantity'])
#             item_total = quantity * rate
#             is_taxable = bool(item.get('is_taxable', False))
#             ledger_id = int(item['ledger_id'])

#             try:
#                 ledger = AccountLedger.objects.get(id=ledger_id)
#             except AccountLedger.DoesNotExist:
#                 return Response(
#                     {"detail": f"Ledger {ledger_id} not found for new item '{key}'."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             clean_title = key.replace('-', ' ')
#             try:
#                 prod = Product.objects.create(
#                     category=category, title=clean_title, is_taxable=is_taxable,
#                     price=rate, ledger=ledger, is_billing_item=False,
#                 )
#             except IntegrityError:
#                 prod = Product.objects.get(title__iexact=clean_title)

#             self.create_subledgers(prod, item_total, ledger_id)
#             ProductPurchase.objects.create(
#                 product=prod, purchase=purchase_object,
#                 quantity=quantity, rate=rate, item_total=item_total,
#             )
#             total_quantity += quantity
#             ledger_totals[ledger_id] = ledger_totals.get(ledger_id, 0) + item_total

#         TblpurchaseEntry.objects.create(
#             bill_no=data.get('bill_no'),
#             bill_date=data.get('bill_date'),
#             pp_no=data.get('pp_no'),
#             vendor_name=vendor.name,
#             vendor_pan=vendor.pan_no,
#             item_name='',
#             quantity=total_quantity,
#             amount=data.get('grand_total'),
#             tax_amount=data.get('tax_amount'),
#             non_tax_purchase=data.get('non_taxable_amount', 0),
#             purchase_id=purchase_object.id,
#         )

#         vendor_detail = f"{vendor.pk} {vendor.name}"

#         if ledger_totals:
#             try:
#                 self.create_accounting_single_ledger(
#                     ledger_totals=ledger_totals,
#                     payment_mode=data.get('payment_mode'),
#                     username=request.user.username,
#                     tax_amount=decimal.Decimal(str(data.get('tax_amount', 0))),
#                     vendor=vendor_detail,
#                     entry_date=data.get('bill_date'),
#                     purchase_object=purchase_object,
#                 )
#             except ValueError as e:
#                 # e.g. bank subledger not found - roll back the whole purchase
#                 transaction.set_rollback(True)
#                 return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#         return Response(
#             {
#                 "id": purchase_object.id,
#                 "bill_no": purchase_object.bill_no,
#                 "grand_total": str(purchase_object.grand_total),
#                 "detail": "Purchase created successfully.",
#             },
#             status=status.HTTP_201_CREATED,
#         )



import decimal
import json
from datetime import datetime

from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from purchase.models import Purchase, ProductPurchase, TblpurchaseEntry
from purchase.utils import update_cumulative_ledger_purchase, create_cumulative_ledger_purchase
from accounting.models import (
    AccountLedger, AccountSubLedger, AccountSubLedgerTracking,
    AccountChart, TblJournalEntry, TblDrJournalEntry, TblCrJournalEntry,
)
from product.models import Product, ProductCategory
from purchase.models import Vendor
from product.models import BranchStock, RequisitionBranchStock


def change_date_to_datetime(entry_date):
    """same helper you already use elsewhere"""
    if isinstance(entry_date, datetime):
        return entry_date
    return datetime.strptime(entry_date, "%Y-%m-%d")


class PurchaseCreateAPI(APIView):
    """
    POST body shape (JSON):

    {
      "bill_no": "PB-001",
      "bill_date": "2026-07-14",
      "pp_no": "PP-001",
      "vendor_id": 3,
      "sub_total": "1000",
      "discount_percentage": "0",
      "discount_amount": "0",
      "taxable_amount": "1000",
      "non_taxable_amount": "0",
      "tax_amount": "130",
      "grand_total": "1130",
      "amount_in_words": "One thousand one hundred thirty only",
      "payment_mode": "credit",           # credit | mobile payment | credit card | complimentary | Bank:<subledger_name> | cash(default)
      "debit_account": 5,                  # default ledger, kept for parity with old view (currently unused downstream)

      "items": [                           # existing products
        {"product_title": "Product A", "quantity": 2, "rate": 100, "total": 200}
      ],

      "new_items": [                       # products that need to be created on the fly
        {
          "key": "cold-drink-500ml",
          "category": "beverages",
          "ledger_id": 5,
          "is_taxable": true,
          "quantity": 3,
          "rate": 50
        }
      ]
    }
    """

    # ---------- helpers (updated with journal linking) ----------

    def create_subledgers(self, product, item_total, ledger_id, journal_entry=None):
        """Create or update subledger for a product purchase with journal linking"""
        debit_account = get_object_or_404(AccountLedger, pk=int(ledger_id))
        subledgername = f'{product.title} ({product.category.title}) - Purchase'
        try:
            sub = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=debit_account)
            prev_value = sub.total_value
            
            # ✅ ADDED: Include journal reference
            tracking = AccountSubLedgerTracking.objects.create(
                subledger=sub,
                prev_amount=prev_value,
                journal=journal_entry  # ✅ Link to journal
            )
            sub.total_value += decimal.Decimal(item_total)
            sub.save()
            tracking.new_amount = sub.total_value
            tracking.value_changed = sub.total_value - prev_value
            tracking.save()
        except AccountSubLedger.DoesNotExist:
            subledger = AccountSubLedger.objects.create(
                sub_ledger_name=subledgername,
                ledger=debit_account,
                total_value=item_total
            )
            # ✅ ADDED: Include journal reference
            tracking = AccountSubLedgerTracking.objects.create(
                subledger=subledger,
                new_amount=decimal.Decimal(item_total),
                value_changed=decimal.Decimal(item_total),
                journal=journal_entry  # ✅ Link to journal
            )

    def create_accounting_single_ledger(self, ledger_totals, payment_mode, username,
                                         tax_amount, vendor, entry_date, purchase_object):
        sub_total = sum(decimal.Decimal(str(total)) for total in ledger_totals.values())
        total_amount = sub_total + tax_amount

        cash_ledger = get_object_or_404(AccountLedger, ledger_name='Cash-In-Hand')
        vat_receivable = get_object_or_404(AccountLedger, ledger_name='VAT Receivable')

        journal_entry = TblJournalEntry.objects.create(
            employee_name=username,
            journal_total=total_amount,
            entry_date=entry_date,
            purchase_journal=purchase_object,
        )

        entry_datetime = change_date_to_datetime(entry_date) if entry_date else datetime.now()

        for ledger_id, amount in ledger_totals.items():
            ledger = get_object_or_404(AccountLedger, pk=int(ledger_id))
            TblDrJournalEntry.objects.create(
                journal_entry=journal_entry,
                particulars=f"Automatic: {ledger.ledger_name} A/c Dr.",
                debit_amount=decimal.Decimal(str(amount)),
                ledger=ledger,
            )
            ledger.total_value += decimal.Decimal(str(amount))
            ledger.save()
            update_cumulative_ledger_purchase(ledger, entry_datetime, journal_entry)

        if tax_amount > 0:
            TblDrJournalEntry.objects.create(
                journal_entry=journal_entry,
                particulars="Automatic: VAT Receivable A/c Dr.",
                debit_amount=tax_amount,
                ledger=vat_receivable,
            )
            vat_receivable.total_value += tax_amount
            vat_receivable.save()
            update_cumulative_ledger_purchase(vat_receivable, entry_datetime, journal_entry)

        mode = payment_mode.lower().strip()

        if mode == "credit":
            try:
                vendor_ledger = AccountLedger.objects.get(ledger_name=vendor)
                vendor_ledger.total_value += total_amount
                vendor_ledger.save()
                update_cumulative_ledger_purchase(vendor_ledger, entry_datetime, journal_entry)
            except AccountLedger.DoesNotExist:
                chart = AccountChart.objects.get(group__iexact='Sundry Creditors')
                vendor_ledger = AccountLedger.objects.create(
                    ledger_name=vendor, total_value=total_amount, is_editable=True, account_chart=chart
                )
                create_cumulative_ledger_purchase(vendor_ledger, entry_datetime, journal_entry)

            TblCrJournalEntry.objects.create(
                journal_entry=journal_entry,
                particulars=f"Automatic: To {vendor_ledger.ledger_name} A/c",
                credit_amount=total_amount,
                ledger=vendor_ledger,
            )

        elif mode in ("mobile payment", "credit card", "complimentary"):
            ledger_name = {
                "mobile payment": "Mobile Payments",
                "credit card": "Card Transactions",
                "complimentary": "Complimentary Expenses",
            }[mode]
            ledger = get_object_or_404(AccountLedger, ledger_name=ledger_name)
            TblCrJournalEntry.objects.create(
                journal_entry=journal_entry,
                particulars=f"Automatic: To {ledger.ledger_name} A/c",
                credit_amount=total_amount,
                ledger=ledger,
            )
            ledger.total_value -= total_amount
            ledger.save()
            update_cumulative_ledger_purchase(ledger, entry_datetime, journal_entry)

        elif payment_mode.startswith("Bank:"):
            subledger_name = payment_mode.replace("Bank:", "").strip()
            bank_account_ledger = get_object_or_404(AccountLedger, ledger_name='Bank Accounts')
            try:
                subledger = AccountSubLedger.objects.get(
                    sub_ledger_name=subledger_name, ledger=bank_account_ledger
                )
            except AccountSubLedger.DoesNotExist:
                raise ValueError(f"Subledger '{subledger_name}' not found under 'Bank Accounts'")

            TblCrJournalEntry.objects.create(
                journal_entry=journal_entry,
                particulars=f"Automatic: To {bank_account_ledger.ledger_name} A/c",
                credit_amount=total_amount,
                ledger=bank_account_ledger,
            )
            bank_account_ledger.total_value -= total_amount
            bank_account_ledger.save()
            update_cumulative_ledger_purchase(bank_account_ledger, entry_datetime, journal_entry)

            prev_value = subledger.total_value
            subledger_tracking = AccountSubLedgerTracking.objects.create(
                subledger=subledger, prev_amount=prev_value, journal=journal_entry
            )
            subledger.total_value -= total_amount
            subledger.save()
            subledger_tracking.new_amount = subledger.total_value
            subledger_tracking.value_changed = subledger.total_value - prev_value
            subledger_tracking.save()

        else:
            TblCrJournalEntry.objects.create(
                journal_entry=journal_entry,
                particulars=f"Automatic: To {cash_ledger.ledger_name} A/c",
                credit_amount=total_amount,
                ledger=cash_ledger,
            )
            cash_ledger.total_value -= total_amount
            cash_ledger.save()
            update_cumulative_ledger_purchase(cash_ledger, entry_datetime, journal_entry)

        # ✅ Return the journal entry so it can be used in subledger tracking
        return journal_entry

    # ---------- validation ----------

    def validate_payload(self, data):
        required = [
            'bill_no', 'bill_date', 'sub_total', 'tax_amount',
            'grand_total', 'payment_mode',
        ]
        missing = [f for f in required if data.get(f) in (None, '')]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"

        items = data.get('items', [])
        new_items = data.get('new_items', [])
        if not items and not new_items:
            return "At least one item (existing or new) is required."

        for i, item in enumerate(items):
            for key in ('product_title', 'quantity', 'rate', 'total'):
                if item.get(key) in (None, ''):
                    return f"items[{i}] missing '{key}'"

        for i, item in enumerate(new_items):
            for key in ('key', 'category', 'ledger_id', 'quantity', 'rate'):
                if item.get(key) in (None, ''):
                    return f"new_items[{i}] missing '{key}'"

        return None

    # ---------- main entrypoint ----------

    @transaction.atomic
    def post(self, request):
        data = request.data

        print("Getting data", data)
        error = self.validate_payload(data)
        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = Vendor.objects.get(name='Aqua Minerals Nepal Pvt Ltd.')
        except Vendor.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        print("We got the branch id as ", data.get("branch"))

        branch_id = data.get("branch")

        purchase_object = Purchase.objects.create(
            bill_no=data.get('bill_no'),
            vendor_id=vendor.id,
            sub_total=data.get('sub_total'),
            bill_date=data.get('bill_date'),
            discount_percentage=data.get('discount_percentage', 0),
            discount_amount=data.get('discount_amount', 0),
            taxable_amount=data.get('taxable_amount', 0),
            non_taxable_amount=data.get('non_taxable_amount', 0),
            tax_amount=data.get('tax_amount', 0),
            grand_total=data.get('grand_total'),
            amount_in_words=data.get('amount_in_words', ''),
            payment_mode=data.get('payment_mode'),
        )

        ledger_totals = {}
        total_quantity = 0

        # ---- First pass: collect ledger totals ----
        # Existing products
        for item in data.get('items', []):
            try:
                product_title = item['product_title']
                quantity = float(item['quantity'])
                rate = float(item['rate'])
                item_total = quantity * rate
                total = float(item['total'])

                prod = Product.objects.get(title=product_title)

                if prod.ledger:
                    ledger_id = prod.ledger.id
                else:
                    ledger_id = AccountLedger.objects.get(ledger_name='Inventory Purchases').id

                ledger_totals[ledger_id] = ledger_totals.get(ledger_id, 0) + total
                total_quantity += quantity

            except (ValueError, KeyError, Product.DoesNotExist, AccountLedger.DoesNotExist):
                continue

        # New products
        for item in data.get('new_items', []):
            key = item['key']
            quantity = float(item['quantity'])
            rate = float(item['rate'])
            item_total = quantity * rate
            ledger_id = int(item['ledger_id'])

            ledger_totals[ledger_id] = ledger_totals.get(ledger_id, 0) + item_total
            total_quantity += quantity

        # ---- Create ONE journal entry with all ledgers ----
        vendor_detail = f"{vendor.pk} {vendor.name}"
        journal_entry_obj = None

        if ledger_totals:
            try:
                journal_entry_obj = self.create_accounting_single_ledger(
                    ledger_totals=ledger_totals,
                    payment_mode=data.get('payment_mode'),
                    username=request.user.username,
                    tax_amount=decimal.Decimal(str(data.get('tax_amount', 0))),
                    vendor=vendor_detail,
                    entry_date=data.get('bill_date'),
                    purchase_object=purchase_object,
                )
            except ValueError as e:
                transaction.set_rollback(True)
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # ---- Second pass: create products and subledgers with journal reference ----
        # Existing products
        for item in data.get('items', []):
            try:
                product_title = item['product_title']
                quantity = float(item['quantity'])
                rate = float(item['rate'])
                item_total = quantity * rate
                total = float(item['total'])

                prod = Product.objects.get(title=product_title)

                if prod.ledger:
                    ledger_id = prod.ledger.id
                else:
                    ledger_id = AccountLedger.objects.get(ledger_name='Inventory Purchases').id

                # ✅ Pass journal_entry_obj to create_subledgers
                self.create_subledgers(prod, item_total, ledger_id, journal_entry_obj)

                ProductPurchase.objects.create(
                    product=prod, purchase=purchase_object,
                    quantity=quantity, rate=rate, item_total=total,
                )

                if branch_id:
                    BranchStock.objects.create(branch_id=data.get("branch"), product_id=prod.id, quantity=quantity)
                    RequisitionBranchStock.objects.create(branch_id=data.get("branch"), product_id=prod.id, quantity=quantity)

            except (ValueError, KeyError, Product.DoesNotExist, AccountLedger.DoesNotExist):
                continue

        # New products
        for item in data.get('new_items', []):
            key = item['key']
            category_name = str(item.get('category', '')).lower().strip()

            category = ProductCategory.objects.filter(title__iexact=category_name).first()
            if not category:
                try:
                    category = ProductCategory.objects.create(title=category_name)
                except IntegrityError:
                    category = ProductCategory.objects.filter(title__iexact=category_name).first()

            rate = float(item['rate'])
            quantity = float(item['quantity'])
            item_total = quantity * rate
            is_taxable = bool(item.get('is_taxable', False))
            ledger_id = int(item['ledger_id'])

            try:
                ledger = AccountLedger.objects.get(id=ledger_id)
            except AccountLedger.DoesNotExist:
                return Response(
                    {"detail": f"Ledger {ledger_id} not found for new item '{key}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            clean_title = key.replace('-', ' ')
            try:
                prod = Product.objects.create(
                    category=category, title=clean_title, is_taxable=is_taxable,
                    price=rate, ledger=ledger, is_billing_item=False,
                )
            except IntegrityError:
                prod = Product.objects.get(title__iexact=clean_title)

            # ✅ Pass journal_entry_obj to create_subledgers
            self.create_subledgers(prod, item_total, ledger_id, journal_entry_obj)

            ProductPurchase.objects.create(
                product=prod, purchase=purchase_object,
                quantity=quantity, rate=rate, item_total=item_total,
            )

            if branch_id:
                BranchStock.objects.create(branch_id=data.get("branch"), product_id=prod.id, quantity=quantity)
                RequisitionBranchStock.objects.create(branch_id=data.get("branch"), product_id=prod.id, quantity=quantity)

        TblpurchaseEntry.objects.create(
            bill_no=data.get('bill_no'),
            bill_date=data.get('bill_date'),
            pp_no=data.get('pp_no'),
            vendor_name=vendor.name,
            vendor_pan=vendor.pan_no,
            item_name='',
            quantity=total_quantity,
            amount=data.get('grand_total'),
            tax_amount=data.get('tax_amount'),
            non_tax_purchase=data.get('non_taxable_amount', 0),
            purchase_id=purchase_object.id,
        )

        return Response(
            {
                "id": purchase_object.id,
                "bill_no": purchase_object.bill_no,
                "grand_total": str(purchase_object.grand_total),
                "detail": "Purchase created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )