from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError

from api.serializers.bill import (
    BillDetailSerializer,
    BillItemSerializer,
    PaymentTypeSerializer,
    BillSerializer,
    TablReturnEntrySerializer,
    TblSalesEntrySerializer,
    TblTaxEntrySerializer,
    TblTaxEntryVoidSerializer
)
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response


from bill.models import Bill, PaymentType, TablReturnEntry, TblSalesEntry, TblTaxEntry, ConflictBillNumber
from organization.models import Branch, Organization

class PaymentTypeList(ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.active()


class BillInfo(APIView):
    def get(self, request):
        branch_code = self.request.query_params.get("branch_code")
        terminal = self.request.query_params.get("terminal")
        branch_and_terminal = f"{branch_code}-{terminal}"
        if not branch_code or not terminal:
            return Response({"result": "Please enter branch code and terminal"},400)
        branch = get_object_or_404(Branch, branch_code=branch_code)
        current_fiscal_year = Organization.objects.last().current_fiscal_year
        last_bill_number = Bill.objects.filter(terminal=terminal, fiscal_year = current_fiscal_year, branch=branch).order_by('-bill_count_number').first()
        if last_bill_number:
            return Response({"result": last_bill_number.invoice_number})
        return Response({"result": 0})



class BillAPI(ModelViewSet):
    serializer_class = BillSerializer
    queryset = Bill.objects.active()

    def get_queryset(self, *args, **kwargs):
        queryset = Bill.objects.filter(
            is_deleted=False, status=True, agent=self.request.user
        )
        return queryset

    def get_serializer_class(self):
        detail_actions = ["retrieve", "list"]
        if self.action in detail_actions:
            return BillDetailSerializer
        return super().get_serializer_class()


    # Temporarily add this to your view to see the error clearly
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("inside bill debug")
        if not serializer.is_valid():
            print("VALIDATION ERRORS:", serializer.errors)  # <-- check terminal
            return Response(serializer.errors, status=400)
        return super().create(request, *args, **kwargs)

class TblTaxEntryAPI(ModelViewSet):
    pagination_class = None
    serializer_class = TblTaxEntrySerializer
    queryset = TblTaxEntry.objects.all()


class TblTaxEntryUpdateView(APIView):
    
    def patch(self, request, bill_no):
        serializer = TblTaxEntryVoidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trans_date = serializer.validated_data.get('trans_date')
        org = Organization.objects.first()
        fiscal_year = org.current_fiscal_year
        try:
            bill_date = trans_date[:10]
            bill_date = datetime.strptime(bill_date, "%Y-%m-%d").date()
        except Exception:
            return Response({'message':'Date time format incorrect'}, status=400)
            

        instance = TblTaxEntry.objects.filter(bill_no=bill_no, bill_date=bill_date)

        if not instance:
            return Response({'message':'No data available with provided details'}, status=404)
        instance = instance.first()

        is_active_data = serializer.validated_data.get("is_active")
        reason = serializer.validated_data.get("reason")


        if is_active_data == "no": 
            miti = ""
            quantity = 1
            try:
                # obj = TblSalesEntry.objects.get(bill_no=instance.bill_no, customer_pan=instance.customer_pan )

                obj = Bill.objects.get(
                    invoice_number=instance.bill_no,
                    customer_tax_number=instance.customer_pan,
                    fiscal_year=fiscal_year
                )
                obj.status = False
                obj.save()
                
                miti = obj.transaction_miti
                quantity = obj.bill_items.count()

                return_entry = TablReturnEntry(
                    bill_date=instance.bill_date,
                    bill_no=instance.bill_no,
                    customer_name=instance.customer_name,
                    customer_pan=instance.customer_pan,
                    amount=instance.amount,
                    NoTaxSales=0,
                    ZeroTaxSales=0,
                    taxable_amount=instance.taxable_amount,
                    tax_amount=instance.tax_amount,
                    miti=miti,
                    ServicedItem="Goods",
                    quantity=quantity,
                    reason=reason,
                )
                return_entry.save()

            except:
                return Response({'message':'Something Went Wrong'}, status=500)
        instance.save()


        return Response({'message':'Successful'})



class TblSalesEntryAPI(ModelViewSet):
    serializer_class = TblSalesEntrySerializer
    queryset = TblSalesEntry.objects.all()


class TablReturnEntryAPI(ModelViewSet):
    serializer_class = TablReturnEntrySerializer
    queryset = TablReturnEntry.objects.all()

class BulkBillCreateView(APIView):

    def post(self, request):
        bills = request.data.get('bills', [])
        if not bills:
            return Response({'details':"Bills is required"}, status=400)
        conflict_invoices = []
        for bill in bills:
            serializer = BillSerializer(data=bill, context={'request':request})
            if serializer.is_valid():
                try:
                    serializer.save()
                except IntegrityError:
                    return Response({'details': "Bill exists with provided details.Integrity Error"}, status=400)
            else:
                conflict_invoices.append(bill['invoice_number'])
                ConflictBillNumber.objects.create(invoice_number=bill['invoice_number'])
        if conflict_invoices:
            return Response({'details': conflict_invoices}, status=409)

        return Response({'details': 'Bills Created'}, status=201)

class BillCheckSumView(APIView):

    def post(self, request):
        fiscal_year = Organization.objects.last().current_fiscal_year

        bills = request.data.get('bills', [])
        if not bills:
            return Response({'details':"Bills is required"}, status=400)
        new_invoice_list:list = []
        for bill in bills:
            invoice_num = bill.get('invoice_number', None)
            fiscal_year = bill.get('fiscal_year', fiscal_year)

            if not Bill.objects.filter(invoice_number=invoice_num, fiscal_year=fiscal_year).exists():
                if bill.get('payment_mode').lower() == "complimentary":
                    if Bill.objects.filter(fiscal_year=fiscal_year, transaction_date_time=bill.get('transaction_date_time')).exists():
                        continue
                new_invoice_list.append(invoice_num)
                serializer = BillSerializer(data=bill, context={'request':request})
                serializer.is_valid(raise_exception=True)
                try:
                    serializer.save()
                except Exception as e:
                    pass
        return Response({'details': 'ok', 'created_invoices':new_invoice_list})
    
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, time
from accounting.models import TblJournalEntry, TblDrJournalEntry, TblCrJournalEntry
from bill.models import Bill  # Replace 'yourapp' with your actual app name
from django.db import transaction

class FixJournalEntryEntryDateForBills(APIView):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        bills = Bill.objects.all().order_by('id')
        updated = 0

        for bill in bills:
            bill_date = bill.created_at.date()
            bill_amount = bill.grand_total

            start_datetime = datetime.combine(bill_date, time.min)
            end_datetime = datetime.combine(bill_date, time.max)

            journal_entry = TblJournalEntry.objects.filter(
                created_at__range=(start_datetime, end_datetime),
                entry_date__isnull=True,
                journal_total=bill_amount,
                employee_name = "Created Automatically during Sale"
            ).order_by('id').first()

            if journal_entry:
                journal_entry.entry_date = bill.transaction_date
                journal_entry.save()
                updated += 1

        return Response({"status": "completed", "updated_entries": updated})
    
from purchase.models import Purchase
class Pur(APIView):
    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        # Get all purchases without a linked journal
        purchases = Purchase.objects.all().order_by('id')
        updated_entries = 0

        for purchase in purchases:
            # Use created_at date instead of bill_date
            purchase_created_date = purchase.created_at.date()
            purchase_total = purchase.grand_total
            print(purchase_created_date)

            start_date = datetime.combine(purchase_created_date, datetime.min.time())
            end_date = datetime.combine(purchase_created_date, datetime.max.time())

            journal_entry = TblJournalEntry.objects.filter(
                created_at__range=(start_date, end_date),
                journal_total=purchase_total
            ).order_by('id').first()

            entry_date = purchase.bill_date
            if journal_entry:
                journal_entry.entry_date = entry_date
                journal_entry.save()

        return Response({"status": "completed", "updated_entries": updated_entries})

            
        

from decimal import Decimal
def give_producttotals(products):
    product_total = 0.0
    product_grandtotal = 0.0
    product_vat = 0.0
    product_quantity = 0

    for product in products:
        product_total += product['total']
        product_grandtotal += product['grand_total']
        product_vat += product['vat']
        product_quantity += product['quantity']

    return product_total, product_grandtotal, product_vat, product_quantity

from django.utils import timezone
from organization.models import Branch, Organization
from bill.models import CreditNote , CreditNoteDetails
from product.models import Product
from django.db import transaction
class AddCreditNote(APIView):
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = request.data

        print(data)
        customer = data['customer']

        products = data['products']
        today_date_str = timezone.now().strftime('%Y-%m-%d')
        from user.models import Customer

        # get organization and branch
        org = Organization.objects.first()
        branch = Branch.objects.filter(is_deleted=False, status=True).first()

        # get totals from the entered products list
        product_total, product_grandtotal, product_vat, product_quantity = give_producttotals(products)

        #Create Credit Note
        creditnote_obj = CreditNote.objects.create(customer_name=customer['customer_name'], 
                                               customer_pan=customer['customer_pan'], 
                                               customer=Customer.objects.get(pk=int(customer['id'])), 
                                               ref_billno=customer['ref_billno'],
                                               quantity= product_quantity,
                                               total =product_total,
                                               grand_total=product_grandtotal,
                                               vat = product_vat,
                                               organization = org,
                                               branch=branch
                                               )
        
        TablReturnEntry.objects.create(
                        customer_name=customer['customer_name'],
                        customer_pan=customer['customer_pan'],
                        taxable_amount=product_total,  # Or calculate based on other fields
                        quantity=product_quantity,
                        bill_date=today_date_str,
                        tax_amount = product_vat,
                        amount = product_grandtotal,
                        bill_no = customer['ref_billno']
                    )
        try:
            for product in products:
                # product['customer_name'] = customer['customer_name']
                # product['customer_pan'] = customer['customer_pan']
                # product['customer'] = Customer.objects.get(pk=int(customer['id']))
                # product['ref_billno'] = customer['ref_billno']
                print(product)
                product_title = product.get('title', None)

                if product_title:
                    if product_title != 'None':
                        product_obj = Product.objects.get(title=product['title']) 
                    else:
                        product_obj = None

                try:
                    CreditNoteDetails.objects.create(product = product_obj, 
                                              rate = product['rate'], 
                                              quantity = product['quantity'], 
                                            #   customer_name=product['customer_name'], 
                                            #   customer_pan = product['customer_pan'], 
                                            #   customer = product['customer'], 
                                              vat = product['vat'], 
                                              total = product['total'],
                                              grand_total = product['grand_total'],
                                              creditnote=creditnote_obj
                                              )
                                            #   ref_billno = product['ref_billno']
                except Exception as e:
                    raise e
                
            return Response({'creditnote':creditnote_obj.id}, 200)
        except Exception as e:
            return Response(e, 400)

# views.py
import json
from datetime import datetime
from django.db import connection, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bill.models import TblSalesEntry  # import your model

@csrf_exempt
@transaction.atomic
def create_bill_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body)

    with connection.cursor() as cursor:
        # 1. Insert into Bill
        cursor.execute("""
            INSERT INTO bill_bill
            (fiscal_year, agent_name, terminal, customer_name,
             customer_address, customer_tax_number, transaction_miti,
             sub_total, discount_amount, taxable_amount, tax_amount,
             grand_total, service_charge, invoice_number, amount_in_words,
             payment_mode, branch_id, customer_id, status, is_deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            data.get("fiscal_year"),
            data.get("agent_name"),
            data.get("terminal"),
            data.get("customer_name"),
            data.get("customer_address"),
            data.get("customer_tax_number"),
            data.get("transaction_miti"),
            data.get("sub_total"),
            data.get("discount_amount"),
            data.get("taxable_amount"),
            data.get("tax_amount"),
            data.get("grand_total"),
            data.get("service_charge"),
            data.get("invoice_number"),
            data.get("amount_in_words"),
            data.get("payment_mode"),
            data.get("branch"),
            data.get("customer"),
            data.get("status"),
            data.get("is_deleted")
        ])
        bill_id = cursor.lastrowid   # ✅ Get inserted Bill ID in MySQL

        billitem_ids = []

        # 2. Insert BillItems
        for item in data.get("bill_items", []):
            cursor.execute("""
                INSERT INTO bill_billitem
                (product_quantity, rate, amount, product_id)
                VALUES (%s, %s, %s, %s)
            """, [
                item["product_quantity"],
                item["rate"],
                item["product_quantity"] * item["rate"],  # calculate amount
                item["product"]
            ])
            billitem_id = cursor.lastrowid   # ✅ Get inserted BillItem ID
            billitem_ids.append(billitem_id)

            # 3. Link Bill and BillItem in M2M table
            cursor.execute("""
                INSERT INTO bill_bill_bill_items (bill_id, billitem_id)
                VALUES (%s, %s)
            """, [bill_id, billitem_id])

    # 4. Create TblSalesEntry record
    TblSalesEntry.objects.create(
        bill_date=datetime.now().strftime("%Y-%m-%d"),
        bill_no=data.get("invoice_number"),
        customer_name=data.get("customer_name"),
        customer_pan=data.get("customer_tax_number"),
        amount=data.get("grand_total"),
        NoTaxSales=0.0,
        ZeroTaxSales=0.0,
        taxable_amount=data.get("taxable_amount"),
        tax_amount=data.get("tax_amount"),
        miti=data.get("transaction_miti"),
        ServicedItem="Goods",
        quantity=1,
        exemptedSales=str(data.get("sub_total") if data.get("tax_amount") == 0 else 0),
    )

    return JsonResponse({
        "bill_id": bill_id,
        "billitem_ids": billitem_ids,
        "sales_entry_created": True
    })


import logging
from datetime import datetime

from django.db import transaction
from django.shortcuts import get_object_or_404
from nepali_datetime import date as nepali_date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounting.views import create_reversing_journal_entry
from accounting.models import TblJournalEntry
from bill.models import IrdCredentials
from rent.models import BillRent

from bill.models import Bill, TablReturnEntry, TblTaxEntry
from bill.ird.postvoidbillintoird import post_credit_note_to_ird

logger = logging.getLogger(__name__)


# class MarkBillVoidAPIView(APIView):
#     """
#     POST /api/bills/<id>/void/
#     Body: { "voidReason": "..." }
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         reason = request.data.get("voidReason", "")
#         bill_id = self.kwargs.get("id")
#         bill = get_object_or_404(Bill, pk=bill_id)

#         if not bill.status:
#             return Response(
#                 {"detail": "This bill is already voided.", "code": "already_voided"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # ---------- STEP 0: Validate void is allowed BEFORE touching IRD or DB ----------
#         if bill.bill_type == Bill.BillType.RENTAL:
#             for item in bill.rental_details.filter(is_deleted=False):
#                 later_exists = (
#                     BillRent.objects.filter(
#                         slot=item.slot,
#                         bill_month__gt=item.bill_month,
#                         is_deleted=False,
#                     )
#                     .exclude(pk=item.pk)
#                     .exists()
#                 )
#                 if later_exists:
#                     return Response(
#                         {
#                             "detail": (
#                                 f"Cannot void: a later bill already exists for slot "
#                                 f"{item.slot.spaceno if item.slot else item.slot_id}. "
#                                 f"Void that bill first."
#                             ),
#                             "code": "later_bill_exists",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#         # ---------- STEP 1: Post credit note to IRD FIRST (before any DB writes) ----------
#         if not bill.branch:
#             return Response(
#                 {
#                     "detail": "Bill has no branch assigned; cannot determine IRD credentials.",
#                     "code": "no_branch",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Scope credentials to this bill's branch. Adjust the filter field name
#         # below to match your actual IrdCredentials model (e.g. `branch=bill.branch`).
#         ird_creds = IrdCredentials.objects.first()

#         ird_response = None
#         ird_skipped = False

#         if not ird_creds:
#             ird_skipped = True
#             logger.warning(
#                 f"No IRD credentials found for branch {bill.branch.branch_code}, skipping IRD post."
#             )
#         else:
#             ad_date = bill.transaction_date
#             bs_date = nepali_date.from_datetime_date(ad_date)
#             bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

#             credit_note_payload = {
#                 "username": ird_creds.username,
#                 "password": ird_creds.password,
#                 "seller_pan": ird_creds.seller_pan,
#                 "buyer_pan": "0",
#                 "fiscal_year": bill.fiscal_year,
#                 "buyer_name": bill.customer_name,
#                 "ref_invoice_number": f"{bill.invoice_number}",
#                 "credit_note_number": f"{bill.branch.branch_code}-VOID-{bill.invoice_number}",
#                 "credit_note_date": bs_date_str,
#                 "reason_for_return": reason if reason else "Voided Bill",
#                 "total_sales": float(bill.grand_total),
#                 "taxable_sales_vat": float(bill.grand_total - bill.tax_amount),
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

#             # ---- Actually call the IRD posting function ----
#             try:
#                 ird_response = post_credit_note_to_ird(credit_note_payload)
#             except Exception as e:
#                 logger.exception(
#                     f"Failed to post credit note to IRD for bill {bill.invoice_number}"
#                 )
#                 return Response(
#                     {
#                         "detail": f"Failed to post credit note to IRD: {str(e)}. "
#                         f"Bill was NOT voided.",
#                         "code": "ird_post_failed",
#                     },
#                     status=status.HTTP_502_BAD_GATEWAY,
#                 )

#             # If your IRD helper returns a success/failure flag or status code inside
#             # the payload rather than raising on failure, check it explicitly here, e.g:
#             if not ird_response or not ird_response.get("success"):
#                 return Response(
#                     {"detail": f"IRD rejected the credit note: {ird_response}",
#                      "code": "ird_rejected"},
#                     status=status.HTTP_502_BAD_GATEWAY,
#                 )

#         # ---------- STEP 2: IRD succeeded (or was skipped) — now do all DB writes atomically ----------
#         journal_warning = None
#         try:
#             with transaction.atomic():
#                 try:
#                     journal_entry = TblJournalEntry.objects.get(bill_id=bill.id)
#                     reversing_journal = create_reversing_journal_entry(
#                         journal_entry.id, request.user.username
#                     )
#                     journal_warning = None
#                     journal_info = f"Reversing journal entry #{reversing_journal.id} created successfully"
#                 except TblJournalEntry.DoesNotExist:
#                     journal_info = None
#                     journal_warning = "No journal entry found to reverse"
#                 except Exception as e:
#                     logger.exception(
#                         f"Error creating reversing journal entry for bill {bill.invoice_number}"
#                     )
#                     journal_info = None
#                     journal_warning = f"Could not create reversing journal entry, but bill will be voided: {str(e)}"

#                 bill.status = False
#                 bill.save()

#                 miti = bill.transaction_miti
#                 quantity = bill.bill_items.count()
#                 return_entry = TablReturnEntry(
#                     bill_date=bill.transaction_date,
#                     bill_no=bill.invoice_number,
#                     customer_name=bill.customer_name,
#                     customer_pan=bill.customer_tax_number,
#                     amount=bill.grand_total,
#                     NoTaxSales=0,
#                     ZeroTaxSales=0,
#                     taxable_amount=bill.taxable_amount,
#                     tax_amount=bill.tax_amount,
#                     miti=miti,
#                     ServicedItem="Goods",
#                     quantity=quantity,
#                     reason=reason,
#                 )
#                 return_entry.save()

#                 if bill.bill_type == Bill.BillType.RENTAL:
#                     updated_count = bill.rental_details.filter(is_deleted=False).update(
#                         is_deleted=True
#                     )
#                     logger.info(
#                         f"Soft-deleted {updated_count} BillRent row(s) for voided rental bill {bill.invoice_number}"
#                     )

#                 try:
#                     entry = TblTaxEntry.objects.get(bill_no=bill.invoice_number)
#                     entry.is_active = "NO"
#                     entry.save()
#                 except TblTaxEntry.DoesNotExist:
#                     pass

#         except Exception as e:
#             logger.exception(
#                 f"Failed to void bill {bill.invoice_number} after IRD post succeeded"
#             )
#             return Response(
#                 {
#                     "detail": (
#                         f"IRD credit note was posted, but voiding the bill failed and "
#                         f"was rolled back: {str(e)}. A credit note may exist on IRD "
#                         f"without a matching void — please investigate manually."
#                     ),
#                     "code": "void_failed_after_ird",
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         response_data = {
#             "detail": "Bill voided successfully.",
#             "bill_id": bill.id,
#             "invoice_number": bill.invoice_number,
#             "ird_skipped": ird_skipped,
#         }
#         if journal_warning:
#             response_data["journal_warning"] = journal_warning
#         if ird_response is not None:
#             response_data["ird_response"] = ird_response

#         return Response(response_data, status=status.HTTP_200_OK)

class MarkBillVoidAPIView(APIView):
    """
    POST /api/bills/<id>/void/
    Body: { "voidReason": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        reason = request.data.get("voidReason", "")
        bill_id = self.kwargs.get("id")
        bill = get_object_or_404(Bill, pk=bill_id)

        if not bill.status:
            return Response(
                {"detail": "This bill is already voided.", "code": "already_voided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------- STEP 0: Validate void is allowed BEFORE touching IRD or DB ----------
        if bill.bill_type == Bill.BillType.RENTAL:
            for item in bill.rental_details.filter(is_deleted=False):
                later_exists = (
                    BillRent.objects.filter(
                        slot=item.slot,
                        bill_month__gt=item.bill_month,
                        is_deleted=False,
                    )
                    .exclude(pk=item.pk)
                    .exists()
                )
                if later_exists:
                    return Response(
                        {
                            "detail": (
                                f"Cannot void: a later bill already exists for slot "
                                f"{item.slot.spaceno if item.slot else item.slot_id}. "
                                f"Void that bill first."
                            ),
                            "code": "later_bill_exists",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # ---------- STEP 1: Post credit note to IRD FIRST (before any DB writes) ----------
        if not bill.branch:
            return Response(
                {
                    "detail": "Bill has no branch assigned; cannot determine IRD credentials.",
                    "code": "no_branch",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Scope credentials to this bill's branch. Adjust the filter field name
        # below to match your actual IrdCredentials model (e.g. `branch=bill.branch`).
        ird_creds = IrdCredentials.objects.first()

        ird_response = None
        ird_skipped = False

        if not ird_creds:
            ird_skipped = True
            logger.warning(
                f"No IRD credentials found for branch {bill.branch.branch_code}, skipping IRD post."
            )
        else:
            ad_date = bill.transaction_date
            bs_date = nepali_date.from_datetime_date(ad_date)
            bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

            credit_note_payload = {
                "username": ird_creds.username,
                "password": ird_creds.password,
                "seller_pan": ird_creds.seller_pan,
                "buyer_pan": "0",
                "fiscal_year": bill.fiscal_year,
                "buyer_name": bill.customer_name,
                "ref_invoice_number": f"{bill.invoice_number}",
                "credit_note_number": f"{bill.branch.branch_code}-VOID-{bill.invoice_number}",
                "credit_note_date": bs_date_str,
                "reason_for_return": reason if reason else "Voided Bill",
                "total_sales": float(bill.grand_total),
                "taxable_sales_vat": float(bill.grand_total - bill.tax_amount),
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

            # # ---- Actually call the IRD posting function ----
            # try:
            #     ird_response = post_credit_note_to_ird(credit_note_payload)
            # except Exception as e:
            #     logger.exception(
            #         f"Failed to post credit note to IRD for bill {bill.invoice_number}"
            #     )
            #     return Response(
            #         {
            #             "detail": f"Failed to post credit note to IRD: {str(e)}. "
            #             f"Bill was NOT voided.",
            #             "code": "ird_post_failed",
            #         },
            #         status=status.HTTP_502_BAD_GATEWAY,
            #     )

            # # If your IRD helper returns a success/failure flag or status code inside
            # # the payload rather than raising on failure, check it explicitly here, e.g:
            # if not ird_response or not ird_response.get("success"):
            #     return Response(
            #         {"detail": f"IRD rejected the credit note: {ird_response}",
            #          "code": "ird_rejected"},
            #         status=status.HTTP_502_BAD_GATEWAY,
            #     )
            print("credit_note_payload",credit_note_payload)
            try:
                ird_response = post_credit_note_to_ird(credit_note_payload)
            except Exception as e:
                logger.exception(
                    f"Failed to post credit note to IRD for bill {bill.invoice_number}"
                )
                return Response(
                    {
                        "detail": f"Failed to post credit note to IRD: {str(e)}. "
                                f"Bill was NOT voided.",
                        "code": "ird_post_failed",
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            if not ird_response.get("success"):
                return Response(
                    {
                        "detail": (
                            f"IRD rejected the credit note: "
                            f"[{ird_response.get('code')}] {ird_response.get('message')}"
                        ),
                        "code": "ird_rejected",
                        "ird_code": ird_response.get("code"),
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        # ---------- STEP 2: IRD succeeded (or was skipped) — now do all DB writes atomically ----------
        journal_warning = None
        try:
            with transaction.atomic():
                try:
                    journal_entry = TblJournalEntry.objects.get(bill_id=bill.id)
                    reversing_journal = create_reversing_journal_entry(
                        journal_entry.id, request.user.username
                    )
                    journal_warning = None
                    journal_info = f"Reversing journal entry #{reversing_journal.id} created successfully"
                except TblJournalEntry.DoesNotExist:
                    journal_info = None
                    journal_warning = "No journal entry found to reverse"
                except Exception as e:
                    logger.exception(
                        f"Error creating reversing journal entry for bill {bill.invoice_number}"
                    )
                    journal_info = None
                    journal_warning = f"Could not create reversing journal entry, but bill will be voided: {str(e)}"

                bill.status = False
                bill.save()

                miti = bill.transaction_miti
                quantity = bill.bill_items.count()
                return_entry = TablReturnEntry(
                    bill_date=bill.transaction_date,
                    bill_no=bill.invoice_number,
                    customer_name=bill.customer_name,
                    customer_pan=bill.customer_tax_number,
                    amount=bill.grand_total,
                    NoTaxSales=0,
                    ZeroTaxSales=0,
                    taxable_amount=bill.taxable_amount,
                    tax_amount=bill.tax_amount,
                    miti=miti,
                    ServicedItem="Goods",
                    quantity=quantity,
                    reason=reason,
                    fiscal_year = bill.fiscal_year
                )
                return_entry.save()

                if bill.bill_type == Bill.BillType.RENTAL:
                    updated_count = bill.rental_details.filter(is_deleted=False).update(
                        is_deleted=True
                    )
                    logger.info(
                        f"Soft-deleted {updated_count} BillRent row(s) for voided rental bill {bill.invoice_number}"
                    )

                try:
                    entry = TblTaxEntry.objects.get(bill_no=bill.invoice_number)
                    entry.is_active = "NO"
                    entry.save()
                except TblTaxEntry.DoesNotExist:
                    pass

        except Exception as e:
            logger.exception(
                f"Failed to void bill {bill.invoice_number} after IRD post succeeded"
            )
            return Response(
                {
                    "detail": (
                        f"IRD credit note was posted, but voiding the bill failed and "
                        f"was rolled back: {str(e)}. A credit note may exist on IRD "
                        f"without a matching void — please investigate manually."
                    ),
                    "code": "void_failed_after_ird",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = {
            "detail": "Bill voided successfully.",
            "bill_id": bill.id,
            "invoice_number": bill.invoice_number,
            "ird_skipped": ird_skipped,
        }
        if journal_warning:
            response_data["journal_warning"] = journal_warning
        if ird_response is not None:
            response_data["ird_response"] = ird_response

        return Response(response_data, status=status.HTTP_200_OK)

class IncrementBillPrintCountAPIView(APIView):
    """
    GET /api/bills/increment-print-count/?bill_id=17
    Increments print_count on the given bill by 1.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bill_id = request.query_params.get('bill_id')
        if not bill_id:
            return Response(
                {"error": "bill_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bill = get_object_or_404(Bill, pk=bill_id)
        bill.print_count += 1
        bill.save(update_fields=['print_count'])

        return Response(
            {"bill_id": bill.id, "print_count": bill.print_count},
            status=status.HTTP_200_OK,
        )

    
from django.db.models import F

class IncrementBillPrintCountBulkAPIView(APIView):
    """
    POST /api/bills/increment-print-count/bulk/
    {
        "bill_ids": [17, 18, 21]
    }
    Increments print_count on each given bill by 1.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        bill_ids = request.data.get('bill_ids')

        if not bill_ids or not isinstance(bill_ids, list):
            return Response(
                {"error": "bill_ids must be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bills = Bill.objects.filter(pk__in=bill_ids)
        found_ids = set(bills.values_list('id', flat=True))
        missing_ids = [bid for bid in bill_ids if bid not in found_ids]

        with transaction.atomic():
            for bill in bills:
                bill.print_count = F('print_count') + 1
                bill.save(update_fields=['print_count'])

        # Refresh to get actual incremented values back (F() expressions
        # don't update the in-memory value after save()).
        updated_bills = Bill.objects.filter(pk__in=found_ids)

        results = [
            {"bill_id": bill.id, "print_count": bill.print_count}
            for bill in updated_bills
        ]

        response_data = {"updated": results}
        if missing_ids:
            response_data["missing_bill_ids"] = missing_ids

        return Response(response_data, status=status.HTTP_200_OK)