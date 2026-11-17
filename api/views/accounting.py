from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from accounting.models import AccountChart, AccountLedger,TblJournalEntry, AccountSubLedger, CumulativeLedger
from purchase.models import DepreciationPool
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from api.serializers.accounting import JournalEntryModelSerializer, AccountLedgerSerializer, AccountLedgerCreateSerializer, AccountSubLedgerCreateSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from organization.models import Organization

@api_view(['PUT'])
def update_account_type(request, pk):
    ac = get_object_or_404(AccountChart, pk=pk)
    ac.account_type=request.query_params.get('accountType')
    ac.save()
    return Response({'Message': 'Successful'})

# @api_view(['PUT'])
# def update_account_ledger(request, pk):
#     subledger = get_object_or_404(AccountLedger, pk=pk)
#     subledger.ledger_name = request.data.get('content', subledger.ledger_name)
#     subledger.save()
#     return Response({'Message': 'Successful'})

@api_view(['PUT'])
def update_account_ledger(request, pk):
    ledger = get_object_or_404(AccountLedger, pk=pk)

    cumulativeledgers = CumulativeLedger.objects.filter(ledger_name= ledger.ledger_name)
    ledger.ledger_name = request.data.get('content', ledger.ledger_name)
    print(ledger.ledger_name)
    # print(cumulativeledger)
    for cumulativeledger in cumulativeledgers:
        cumulativeledger.ledger_name = request.data.get('content', cumulativeledger.ledger_name)
        cumulativeledger.save()
    ledger.save()
    return Response({'Message': 'Successful'})

@api_view(['PUT'])
def update_account_group(request, pk):
    ledger = get_object_or_404(AccountChart, pk=pk)
    ledger.group = request.data.get('content', ledger.group)
    ledger.save()
    return Response({'Message': 'Successful'})

@api_view(['PUT'])
def update_account_subledger(request, pk):
    sub_ledger = get_object_or_404(AccountSubLedger, pk=pk)
    sub_ledger.sub_ledger_name = request.data.get('content', sub_ledger.sub_ledger_name)
    sub_ledger.save()
    return Response({'Message': 'Successful'})

@api_view(['GET'])
def get_depreciation_pool(request):
    data = DepreciationPool.objects.all().values()
    return Response({'data':data})


# class ChartOfAccountAPIView(APIView):
#     def get(self, request):
#         data = {}
#         org = Organization.objects.all()
#         if org:
#             o = org.first()
#             data['organization'] = {"name":o.org_name, "email":o.company_contact_email, "address": o.company_address}
#         account_chart = AccountChart.objects.all()
#         for ac in account_chart:
#             if ac.account_type not in data:
#                 data[ac.account_type] = {"groups":[]}
#             data[ac.account_type]["groups"].append({"group_name":ac.group, "ledgers":[]})
#             for ledger in ac.accountledger_set.all():
#                 data[ac.account_type]["groups"][-1]['ledgers'].append({"name":ledger.ledger_name, "total_value":ledger.total_value, "sub_ledgers":[]})
#                 for subl in ledger.accountsubledger_set.all():
#                     data[ac.account_type]["groups"][-1]['ledgers'][-1]["sub_ledgers"].append({"name":subl.sub_ledger_name, "value":subl.total_value})

#         return Response(data)

class ChartOfAccountAPIView(APIView):
    def get(self, request):
        data = {}
        org = Organization.objects.all()
        if org:
            o = org.first()
            data['organization'] = {"name":o.org_name, "email":o.company_contact_email, "address": o.company_address}
        account_chart = AccountChart.objects.all()
        for ac in account_chart:
            if ac.account_type not in data:
                data[ac.account_type] = {"groups":[]}
            data[ac.account_type]["groups"].append({"group_id":ac.id, "group_name":ac.group, "ledgers":[]})
            for ledger in ac.accountledger_set.all():
                data[ac.account_type]["groups"][-1]['ledgers'].append({"ledger_id": ledger.id, "name":ledger.ledger_name, "total_value":ledger.total_value, "sub_ledgers":[]})
                for subl in ledger.accountsubledger_set.all():
                    data[ac.account_type]["groups"][-1]['ledgers'][-1]["sub_ledgers"].append({"sub_ledger_id": subl.id, "name":subl.sub_ledger_name, "value":subl.total_value})

        return Response(data)
    

class JournalEntryAPIView(ListAPIView):
    queryset = TblJournalEntry.objects.all()
    serializer_class = JournalEntryModelSerializer

    def list(self, request, *args, **kwargs):
        from_date = self.request.query_params.get('fromDate')
        to_date = self.request.query_params.get('toDate')
        if from_date and to_date:
            queryset = TblJournalEntry.objects.filter(created_at__range=[from_date, to_date])
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = TblJournalEntry.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)


class TrialBalanceAPIView(APIView):

    permission_classes = IsAuthenticated, 

    def get(self, request):
        trial_balance = []
        total = {'debit_total':0, 'credit_total':0}
        ledgers = AccountLedger.objects.filter(total_value__gt=0)
        for led in ledgers:
            data = {}
            data['ledger']=led.ledger_name
            account_type = led.account_chart.account_type
            data['account_head']=account_type

            if account_type in ['Asset', 'Expense']:
                if led.total_value > 0:
                    data['debit'] = led.total_value
                    total['debit_total'] += led.total_value
                    data['credit'] = '-'
                else:
                    data['credit'] = led.total_value
                    total['credit_total'] += led.total_value
                    data['debit'] = '-'
            else:
                if led.total_value > 0:
                    data['credit'] = led.total_value
                    total['credit_total'] += led.total_value
                    data['debit'] = '-'
                else:
                    data['debit'] = led.total_value
                    total['debit_total'] += led.total_value
                    data['credit'] = '-'
            trial_balance.append(data)

        vat_receivable, vat_payable = 0, 0
        for data in trial_balance:
            if data['ledger'] == 'VAT Receivable':
                vat_receivable = data['debit']
                total['debit_total'] -= data['debit']
                trial_balance.remove(data)
            if data['ledger'] == 'VAT Payable':
                vat_payable = data['credit']
                total['credit_total'] -= data['credit']
                trial_balance.remove(data)
        vat_amount = vat_receivable - vat_payable
        if vat_amount > 0:
            trial_balance.append({'ledger':'VAT', 'account_head':'Asset', 'debit':vat_amount, 'credit':'-'})
            total['debit_total'] += vat_amount
        elif vat_amount < 0:
            trial_balance.append({'ledger':'VAT', 'account_head':'Liability', 'debit':'-', 'credit':abs(vat_amount)})
            total['credit_total'] += abs(vat_amount)

        trial_balance = sorted(trial_balance, key=lambda x:x['account_head'])
        context = {
            'trial_balance': trial_balance,
            "total": total
        }
        return Response(context)


class ProfitAndLossAPIView(APIView):

    def get(self, request):
        expense = AccountLedger.objects.filter(account_chart__account_type="Expense")
        income = AccountLedger.objects.filter(account_chart__account_type="Revenue")
        expense_serializer = AccountLedgerSerializer(expense, many=True)
        income_serializer = AccountLedgerSerializer(income, many=True)
        total_income, total_expense = 0, 0

        for income in income_serializer.data:
            total_income += float(income['total_value'])
        
        for expense in expense_serializer.data:
            total_expense += float(expense['total_value'])

        data = {
            "income":income_serializer.data,
            "expense": expense_serializer.data,
            "total_income": total_income,
            "total_expense":total_expense
        }
        return Response(data)
    

class BalanceSheetAPIView(APIView):
    #permission_classes = IsAdminUser,
    def get(self, request):
        print(request.user.is_staff)
        context = {}
        asset_dict = {
            "groups":[]
        }
        liability_dict = {
            "groups": []
        }

        assets = AccountChart.objects.filter(account_type='Asset')
        for ledger in assets:
            sub = AccountLedger.objects.filter(account_chart__group=ledger, total_value__gt=0)
            if sub:
                asset_dict['groups'].append({
                    "title":ledger.group,
                    "ledgers": []

                })
                for s in sub:
                    subledger = model_to_dict(s)
                    del subledger['id']
                    del subledger['account_chart']
                    del subledger['is_editable']
                    asset_dict['groups'][-1]["ledgers"].append(subledger)

        liabilities = AccountChart.objects.filter(Q(account_type="Liability") | Q(account_type="Equity") )
        for ledger in liabilities:
            sub = AccountLedger.objects.filter(account_chart__group=ledger, total_value__gt=0)
            if sub:
                liability_dict['groups'].append({
                    "title":ledger.group,
                    "ledgers": []

                })
                for s in sub:
                    subledger = model_to_dict(s)
                    del subledger['id']
                    del subledger['account_chart']
                    del subledger['is_editable']
                    liability_dict['groups'][-1]["ledgers"].append(subledger)

        asset_total = AccountLedger.objects.filter(account_chart__account_type='Asset').aggregate(Sum('total_value')).get('total_value__sum')
        liability_total = AccountLedger.objects.filter(Q(account_chart__account_type="Liability") | Q(account_chart__account_type="Equity") )\
                                    .aggregate(Sum('total_value')).get('total_value__sum')
        

        if asset_total and liability_total:
            if asset_total > liability_total:
                context['retained_earnings'] =  asset_total-liability_total
                context['retained_loss'] = 0
                context['liability_total'] = liability_total + asset_total-liability_total
                context['asset_total'] = asset_total

            else:
                context['retained_loss'] =  liability_total-asset_total
                context['retained_earnings'] = 0
                context['asset_total'] = asset_total + liability_total-asset_total
                context['liability_total'] = liability_total
            

        context['assets'] = asset_dict
        context['liabilities'] =  liability_dict
        return Response(context)

class LedgersAPIView(APIView):
    def get(self, request):
        ledgers = AccountLedger.objects.all()

        serializer = AccountLedgerSerializer(ledgers, many=True)

        return Response(serializer.data, 200)

from api.serializers.accounting import AccountSubLedgerSerializer
class SubLedgersAPI(APIView):
    def post(self, request, *args, **kwargs):
        ledger_name = request.data['ledger']

        ledger = AccountLedger.objects.get(ledger_name=ledger_name)
        if Organization.objects.first().show_zero_ledgers:

            subledgers = AccountSubLedger.objects.filter(ledger=ledger)
        else:
            subledgers = AccountSubLedger.objects.filter(ledger=ledger, total_value__gt=0.0)

        serializer = AccountSubLedgerSerializer(subledgers, many=True)

        return Response(serializer.data, 200)
    
from api.serializers.accounting import AccountSubLedgerSerializer
class ExpenseSubLedgersAPI(APIView):
    def post(self, request, *args, **kwargs):
        ledger_id = request.data['ledger']

        ledger = AccountLedger.objects.get(id=ledger_id)
        if Organization.objects.first().show_zero_ledgers:

            subledgers = AccountSubLedger.objects.filter(ledger=ledger)
        else:
            subledgers = AccountSubLedger.objects.filter(ledger=ledger)

        serializer = AccountSubLedgerSerializer(subledgers, many=True)

        return Response(serializer.data, 200)
    
class SundryLedgersAPI(APIView):
    def post(self, request, *args, **kwargs):
        group_name = request.data['group']

        # ledger = AccountLedger.objects.get(account_chart__group=group_name)
        if Organization.objects.first().show_zero_ledgers:

            ledgers = AccountLedger.objects.filter(account_chart__group=group_name)
        else:
            ledgers = AccountLedger.objects.filter(account_chart__group=group_name, total_value__gt=0.0)

        serializer = AccountLedgerSerializer(ledgers, many=True)

        return Response(serializer.data, 200)

from django.db.models import Q
from api.serializers.accounting import AccountLedgerWithSubLedgerSerializer
class AccountLedgerWithSubledgersAPIView(APIView):
    def get(self, request, *args, **kwargs):

        accountledgers = AccountLedger.objects.filter(Q(ledger_name="Bank Accounts") | Q(ledger_name = "Cash-In-Hand"))

        serializer = AccountLedgerWithSubLedgerSerializer(accountledgers, many=True)


        return Response(serializer.data, 200)

from rest_framework.generics import ListAPIView, CreateAPIView
from accounting.models import AccountChart
from api.serializers.accounting import AccountChartSerializer


class AccountChartListAPI(ListAPIView):
    queryset = AccountChart.objects.all().order_by('group')
    serializer_class = AccountChartSerializer
    pagination_class = None


class AccountChartCreateAPI(CreateAPIView):
    queryset = AccountChart.objects.all()
    serializer_class = AccountChartSerializer

from datetime import datetime, timedelta
import pytz
from rest_framework.generics import CreateAPIView

from bill.utils import create_cumulative_ledger_accounting
class AccountLedgerCreateAPI(CreateAPIView):
    queryset = AccountLedger.objects.all()
    serializer_class = AccountLedgerCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        nepal_tz = pytz.timezone("Asia/Kathmandu")

        today = datetime.now().date()
        naive_datetime = datetime.combine(today, datetime.min.time())
        nepal_datetime = nepal_tz.localize(naive_datetime)
        entry_date = nepal_datetime + timedelta(hours=5, minutes=45)

        create_cumulative_ledger_accounting(instance, entry_date)


from django.db import transaction
from django.utils import timezone

from rest_framework.generics import CreateAPIView
from rest_framework import serializers

from accounting.models import AccountSubLedger, AccountSubLedgerTracking
from bill.utils import update_cumulative_ledger_accounting

from rest_framework import status
class AccountSubLedgerCreateAPI(CreateAPIView):
    queryset = AccountSubLedger.objects.all()
    serializer_class = AccountSubLedgerCreateSerializer

    def create(self, request, *args, **kwargs):
        data_list = request.data if isinstance(request.data, list) else [request.data]

        results = []
        with transaction.atomic():
            for item_data in data_list:
                serializer = self.get_serializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                subledger = self.perform_create(serializer)
                results.append(subledger)

        output_serializer = self.get_serializer(results, many=True)
        headers = {}
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        subledger = serializer.save()

        ledger = subledger.ledger

        prev_value = 0
        entered_value = subledger.total_value

        is_only_subledger = AccountSubLedger.objects.filter(ledger=ledger).count() == 1

        if is_only_subledger and ledger.total_value != 0:
            new_value = entered_value + ledger.total_value
            subledger.total_value = new_value
            subledger.save(update_fields=['total_value'])
        else:
            new_value = entered_value
            ledger.total_value = ledger.total_value + new_value
            ledger.save()

        AccountSubLedgerTracking.objects.create(
            subledger=subledger,
            prev_amount=prev_value,
            new_amount=new_value,
            value_changed=new_value - prev_value
        )

        entry_datetime_forcumulativeledger = timezone.now()
        update_cumulative_ledger_accounting(ledger, entry_datetime_forcumulativeledger)

        return subledger
    

class LedgerWithSubLedgersCreateAPI(APIView):
    """
    Payload shape:
    {
        "ledger": {
            "id": 5,                    # OPTIONAL: if present, use existing ledger
            "ledger_name": "...",       # required only when creating new ledger
            "account_chart": 1,         # required only when creating new ledger
        },
        "subledgers": [
            {"sub_ledger_name": "Cash in Hand", "total_value": 5000},
            {"sub_ledger_name": "Petty Cash", "total_value": 1500}
        ]
    }
    """

    def post(self, request, *args, **kwargs):
        ledger_data = request.data.get('ledger', {})
        subledgers_data = request.data.get('subledgers', [])

        if not subledgers_data:
            return Response(
                {"detail": "At least one subledger is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            ledger, ledger_created = self._get_or_create_ledger(ledger_data)

            created_subledgers = []
            for item_data in subledgers_data:
                item_data = dict(item_data)
                item_data['ledger'] = ledger.id

                serializer = AccountSubLedgerCreateSerializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                subledger = self._create_subledger(serializer, ledger)
                created_subledgers.append(subledger)

        ledger_serializer = AccountLedgerCreateSerializer(ledger)
        subledger_serializer = AccountSubLedgerCreateSerializer(created_subledgers, many=True)

        return Response(
            {
                "ledger": ledger_serializer.data,
                "ledger_created": ledger_created,
                "subledgers": subledger_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def _get_or_create_ledger(self, ledger_data):
        ledger_id = ledger_data.get('id')

        if ledger_id:
            try:
                ledger = AccountLedger.objects.get(id=ledger_id)
            except AccountLedger.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"ledger": f"Ledger with id {ledger_id} does not exist."})
            return ledger, False

        serializer = AccountLedgerCreateSerializer(data=ledger_data)
        serializer.is_valid(raise_exception=True)
        ledger = serializer.save()

        nepal_tz = pytz.timezone("Asia/Kathmandu")
        today = datetime.now().date()
        naive_datetime = datetime.combine(today, datetime.min.time())
        nepal_datetime = nepal_tz.localize(naive_datetime)
        entry_date = nepal_datetime + timedelta(hours=5, minutes=45)

        create_cumulative_ledger_accounting(ledger, entry_date)

        return ledger, True

    def _create_subledger(self, serializer, ledger):
        subledger = serializer.save()

        prev_value = 0
        entered_value = subledger.total_value

        is_only_subledger = AccountSubLedger.objects.filter(ledger=ledger).count() == 1

        if is_only_subledger and ledger.total_value != 0:
            new_value = entered_value + ledger.total_value
            subledger.total_value = new_value
            subledger.save(update_fields=['total_value'])
        else:
            new_value = entered_value
            ledger.total_value = ledger.total_value + new_value
            ledger.save()

        AccountSubLedgerTracking.objects.create(
            subledger=subledger,
            prev_amount=prev_value,
            new_amount=new_value,
            value_changed=new_value - prev_value
        )

        entry_datetime_forcumulativeledger = timezone.now()
        update_cumulative_ledger_accounting(ledger, entry_datetime_forcumulativeledger)

        return subledger



from accounting.detail_utils import give_detail, get_standard_trial_balance
from user.permission import IsAdminMixin

# class TrialBalanceLedgerAPIView(APIView):
#     """
#     API endpoint that returns ledger-level trial balance data with full date filtering
#     and open/close functionality
#     """
    
#     def get(self, request):
#         # Get query parameters
#         from_date = request.GET.get('fromDate', None)
#         to_date = request.GET.get('toDate', None)
#         option = request.GET.get('option', None)
#         date_type = request.GET.get('date_type', 'entry_date')
#         show_zero_ledgers = request.GET.get('show_zero_ledgers', 'false').lower() == 'true'
        
#         # Get organization settings
#         org = Organization.objects.first()
#         if not org:
#             return Response(
#                 {"error": "No organization found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         current_fiscal_year = org.current_fiscal_year
#         show_zero = show_zero_ledgers or org.show_zero_ledgers
        
#         try:
#             # Initialize variables
#             trial_balance = []
#             total = {'debit_total': 0, 'credit_total': 0}
            
#             # Case 1: Both from_date and to_date provided
#             if from_date and to_date:
#                 # Case 1a: Open/Close option - use the existing give_detail function
#                 if option and option == 'openclose':
#                     trial_balance, total = give_detail(from_date, to_date)
#                 # Case 1b: Regular date filtered trial balance
#                 else:
#                     # For date filtering without open/close, we need to use the existing logic
#                     # but the original code doesn't have date filtering for non-open/close
#                     # Let's use give_detail which handles date filtering
#                     trial_balance, total = give_detail(from_date, to_date)
#             # Case 2: No dates provided - get all data
#             else:
#                 trial_balance, total = self.get_all_ledgers(show_zero)
            
#             # Extract complete ledger data including Sundry and VAT
#             ledger_data, total = self.extract_complete_ledger_data(
#                 trial_balance, total, show_zero
#             )
            
#             # Prepare response
#             response_data = {
#                 'success': True,
#                 'data': {
#                     'ledgers': ledger_data,
#                     'summary': {
#                         'total_ledgers': len(ledger_data),
#                         'total_debit': round(total.get('debit_total', 0), 2),
#                         'total_credit': round(total.get('credit_total', 0), 2),
#                         'difference': round(total.get('debit_total', 0) - total.get('credit_total', 0), 2),
#                         'is_balanced': abs(total.get('debit_total', 0) - total.get('credit_total', 0)) < 0.01
#                     }
#                 },
#                 'filters': {
#                     'from_date': from_date,
#                     'to_date': to_date,
#                     'option': option,
#                     'date_type': date_type,
#                     'show_zero_ledgers': show_zero,
#                     'current_fiscal_year': current_fiscal_year
#                 }
#             }
            
#             return Response(response_data, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             return Response(
#                 {
#                     "success": False, 
#                     "error": str(e),
#                     "traceback": traceback.format_exc()
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     def get_all_ledgers(self, show_zero):
#         """
#         Get all ledgers without date filtering (replicates your original logic)
#         """
#         # Get ledgers excluding VAT
#         if show_zero:
#             ledgers = AccountLedger.objects.filter(
#                 ~Q(ledger_name='VAT Receivable'),
#                 ~Q(ledger_name='VAT Payable')
#             )
#         else:
#             ledgers = AccountLedger.objects.filter(
#                 ~Q(total_value=0),
#                 ~Q(ledger_name='VAT Receivable'),
#                 ~Q(ledger_name='VAT Payable')
#             )
        
#         total = {'debit_total': 0, 'credit_total': 0}
#         ledger_dict = {}
        
#         for led in ledgers:
#             data = {}
#             account_type = led.account_chart.account_type
#             account_group = led.account_chart.group
#             data['account_type'] = account_type
#             data['ledger_name'] = led.ledger_name
#             data['account_group'] = account_group
#             data['ledger_id'] = led.id
#             data['total_value'] = led.total_value
            
#             # Get subledgers
#             if show_zero:
#                 subledgers = AccountSubLedger.objects.filter(ledger_id=led.id)
#             else:
#                 subledgers = AccountSubLedger.objects.filter(
#                     ledger_id=led.id, 
#                     total_value__gt=0.0
#                 )
            
#             subledger_entries = []
#             for subledger in subledgers:
#                 subledger_data = {
#                     'subledger_id': subledger.id,
#                     'subledger_name': subledger.sub_ledger_name,
#                     'total_value': subledger.total_value
#                 }
#                 subledger_entries.append(subledger_data)
#             data['subledgers'] = subledger_entries
            
#             # Calculate debit/credit based on account type
#             debit = 0
#             credit = 0
            
#             if account_type in ['Asset', 'Expense']:
#                 if led.total_value > 0:
#                     debit = led.total_value
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['debit_total'] += led.total_value
#                 else:
#                     credit = abs(led.total_value)
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['credit_total'] += abs(led.total_value)
#             else:
#                 if led.total_value > 0:
#                     credit = led.total_value
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['credit_total'] += led.total_value
#                 else:
#                     debit = abs(led.total_value)
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['debit_total'] += abs(led.total_value)
            
#             data['debit'] = debit
#             data['credit'] = credit
            
#             # Use ledger name as key to avoid redundancy
#             ledger_name = data['ledger_name']
#             if ledger_name not in ledger_dict:
#                 ledger_dict[ledger_name] = data
        
#         # Convert to list
#         ledger_list = list(ledger_dict.values())
        
#         # Group by account type for compatibility with extract function
#         trial_balance = self.group_ledgers_by_account_type(ledger_list)
        
#         # Handle VAT
#         self.handle_vat(trial_balance, total, show_zero)
        
#         return trial_balance, total
    
#     def group_ledgers_by_account_type(self, ledger_list):
#         """
#         Group ledgers by account type and group (replicates your original grouping logic)
#         """
#         trial_balance = []
        
#         for entry in ledger_list:
#             real_account_type = entry['account_type']
#             account_type = entry['account_group']
#             account_group = entry['account_group']
            
#             # Check if the account_type already exists in trial_balance
#             account_type_entry = next((d for d in trial_balance if d['account_type'] == account_type), None)
            
#             if not account_type_entry:
#                 trial_balance.append({
#                     'real_account_type': real_account_type, 
#                     'account_type': account_type, 
#                     'groups': [{'group': account_group, 'ledgers': [entry]}]
#                 })
#             else:
#                 # Find the dictionary for the current account_type
#                 current_account_type = next((d for d in trial_balance if d['account_type'] == account_type), None)
                
#                 # Check if the account_group already exists for the current account_type
#                 account_group_entry = next((g for g in current_account_type['groups'] if g['group'] == account_group), None)
                
#                 if not account_group_entry:
#                     current_account_type['groups'].append({'group': account_group, 'ledgers': [entry]})
#                 else:
#                     account_group_entry['ledgers'].append(entry)
        
#         return trial_balance
    
#     def handle_vat(self, trial_balance, total, show_zero):
#         """
#         Handle VAT calculation (replicates your original VAT logic)
#         """
#         try:
#             vat_receivable = AccountLedger.objects.get(ledger_name='VAT Receivable')
#             vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
            
#             vat_receivable_val = vat_receivable.total_value
#             vat_payable_val = vat_payable.total_value
            
#             vat = vat_receivable_val - vat_payable_val
            
#             if vat > 0:
#                 vatreceivable_subledgers = AccountSubLedger.objects.filter(
#                     ledger__ledger_name='VAT Receivable'
#                 )
#                 vatreceivable_subledger_entries = []
#                 for subledger in vatreceivable_subledgers:
#                     subledger_data = {
#                         'subledger_id': subledger.id,
#                         'subledger_name': subledger.sub_ledger_name,
#                         'total_value': subledger.total_value
#                     }
#                     vatreceivable_subledger_entries.append(subledger_data)
                
#                 new_vat_receivable_entry = {
#                     'real_account_type': vat_receivable.account_chart.account_type,
#                     'account_type': vat_receivable.account_chart.group,
#                     'groups': [{
#                         'group': vat_receivable.account_chart.group,
#                         'ledgers': [{
#                             'ledger_id': vat_receivable.id,
#                             'ledger_name': vat_receivable.ledger_name,
#                             'account_type': vat_receivable.account_chart.account_type,
#                             'account_group': vat_receivable.account_chart.group,
#                             'debit': abs(vat),
#                             'credit': 0,
#                             'total_value': abs(vat),
#                             'subledgers': vatreceivable_subledger_entries,
#                             'has_subledgers': len(vatreceivable_subledger_entries) > 0
#                         }]
#                     }]
#                 }
#                 total['debit_total'] += abs(vat)
#                 trial_balance.append(new_vat_receivable_entry)
#             elif vat < 0:
#                 vatpayable_subledgers = AccountSubLedger.objects.filter(
#                     ledger__ledger_name='VAT Payable'
#                 )
#                 vatpayable_subledger_entries = []
#                 for subledger in vatpayable_subledgers:
#                     subledger_data = {
#                         'subledger_id': subledger.id,
#                         'subledger_name': subledger.sub_ledger_name,
#                         'total_value': subledger.total_value
#                     }
#                     vatpayable_subledger_entries.append(subledger_data)
                
#                 new_vat_payable_entry = {
#                     'real_account_type': vat_payable.account_chart.account_type,
#                     'account_type': vat_payable.account_chart.group,
#                     'groups': [{
#                         'group': vat_payable.account_chart.group,
#                         'ledgers': [{
#                             'ledger_id': vat_payable.id,
#                             'ledger_name': vat_payable.ledger_name,
#                             'account_type': vat_payable.account_chart.account_type,
#                             'account_group': vat_payable.account_chart.group,
#                             'debit': 0,
#                             'credit': abs(vat),
#                             'total_value': abs(vat),
#                             'subledgers': vatpayable_subledger_entries,
#                             'has_subledgers': len(vatpayable_subledger_entries) > 0
#                         }]
#                     }]
#                 }
#                 total['credit_total'] += abs(vat)
#                 trial_balance.append(new_vat_payable_entry)
                
#         except AccountLedger.DoesNotExist:
#             pass
    
#     def extract_complete_ledger_data(self, trial_balance, total, show_zero):
#         """
#         Extract complete ledger data including Sundry Debtors, Creditors, and VAT
#         """
#         all_ledgers = []
        
#         # Initialize sundry totals
#         sundry_debtors_debit_total = 0
#         sundry_debtors_credit_total = 0
#         sundry_creditors_debit_total = 0
#         sundry_creditors_credit_total = 0
        
#         # First pass: Calculate sundry totals and collect regular ledgers
#         for entry in trial_balance:
#             if 'groups' in entry:
#                 for group in entry['groups']:
#                     if 'ledgers' in group:
#                         # Filter out sundry ledgers and collect regular ones
#                         new_ledger_entries = []
#                         for ledger in group['ledgers']:
#                             account_group = ledger.get('account_group', '')
                            
#                             if account_group == 'Sundry Debtors':
#                                 debit = ledger.get('debit', 0)
#                                 credit = ledger.get('credit', 0)
#                                 if debit != '-':
#                                     sundry_debtors_debit_total += debit
#                                 if credit != '-':
#                                     sundry_debtors_credit_total += credit
#                             elif account_group == 'Sundry Creditors':
#                                 debit = ledger.get('debit', 0)
#                                 credit = ledger.get('credit', 0)
#                                 if debit != '-':
#                                     sundry_creditors_debit_total += debit
#                                 if credit != '-':
#                                     sundry_creditors_credit_total += credit
#                             else:
#                                 # Add regular ledger
#                                 new_ledger_entries.append(self.format_ledger_for_api(ledger))
                        
#                         # Update group with filtered ledgers
#                         group['ledgers'] = new_ledger_entries
        
#         # Add Sundry Debtors
#         sundry_debtors_total = sundry_debtors_debit_total - sundry_debtors_credit_total
#         if sundry_debtors_total != 0 or show_zero:
#             sundry_debtors_entry = self.create_sundry_entry(
#                 'Sundry Debtors',
#                 sundry_debtors_total,
#                 'Asset',
#                 show_zero
#             )
#             if sundry_debtors_entry:
#                 all_ledgers.append(sundry_debtors_entry)
#                 if sundry_debtors_total > 0:
#                     total['debit_total'] += sundry_debtors_total
#                 else:
#                     total['credit_total'] += abs(sundry_debtors_total)
        
#         # Add Sundry Creditors
#         sundry_creditors_total = sundry_creditors_credit_total - sundry_creditors_debit_total
#         if sundry_creditors_total != 0 or show_zero:
#             sundry_creditors_entry = self.create_sundry_entry(
#                 'Sundry Creditors',
#                 sundry_creditors_total,
#                 'Liability',
#                 show_zero
#             )
#             if sundry_creditors_entry:
#                 all_ledgers.append(sundry_creditors_entry)
#                 if sundry_creditors_total > 0:
#                     total['credit_total'] += sundry_creditors_total
#                 else:
#                     total['debit_total'] += abs(sundry_creditors_total)
        
#         # Collect remaining regular ledgers from trial_balance
#         for entry in trial_balance:
#             if 'groups' in entry:
#                 for group in entry['groups']:
#                     if 'ledgers' in group:
#                         for ledger in group['ledgers']:
#                             if ledger:
#                                 # Skip if it's sundry or VAT (already handled)
#                                 account_group = ledger.get('account_group', '')
#                                 if account_group not in ['Sundry Debtors', 'Sundry Creditors']:
#                                     all_ledgers.append(self.format_ledger_for_api(ledger))
        
#         # Sort by account type and name
#         all_ledgers.sort(key=lambda x: (x['account_type'], x['ledger_name']))
        
#         return all_ledgers, total
    
#     def format_ledger_for_api(self, ledger):
#         """Format ledger data for API response"""
#         return {
#             'ledger_id': ledger.get('ledger_id', None),
#             'ledger_name': ledger.get('ledger_name', ''),
#             'account_type': ledger.get('account_type', ''),
#             'account_group': ledger.get('account_group', ''),
#             'debit': round(ledger.get('debit', 0) if ledger.get('debit', 0) != '-' else 0, 2),
#             'credit': round(ledger.get('credit', 0) if ledger.get('credit', 0) != '-' else 0, 2),
#             'total_value': round(ledger.get('total_value', 0), 2),
#             'subledgers': ledger.get('subledgers', []),
#             'has_subledgers': len(ledger.get('subledgers', [])) > 0
#         }
    
#     def create_sundry_entry(self, name, total, account_type, show_zero):
#         """Create a sundry entry (Debtors or Creditors)"""
#         # Get all subledgers for this sundry group
#         ledgers = AccountLedger.objects.filter(account_chart__group=name)
#         subledger_entries = []
        
#         for ledger in ledgers:
#             if show_zero or ledger.total_value != 0:
#                 subledger_data = {
#                     'subledger_id': ledger.id,
#                     'subledger_name': ledger.ledger_name,
#                     'total_value': round(ledger.total_value, 2)
#                 }
#                 subledger_entries.append(subledger_data)
        
#         # Determine debit and credit
#         debit = 0
#         credit = 0
        
#         if name == 'Sundry Debtors':
#             if total > 0:
#                 debit = total
#             else:
#                 credit = abs(total)
#         else:  # Sundry Creditors
#             if total > 0:
#                 credit = total
#             else:
#                 debit = abs(total)
        
#         return {
#             'ledger_id': None,
#             'ledger_name': name,
#             'account_type': account_type,
#             'account_group': name,
#             'debit': round(debit, 2),
#             'credit': round(credit, 2),
#             'total_value': round(total, 2),
#             'subledgers': subledger_entries,
#             'has_subledgers': len(subledger_entries) > 0,
#             'is_sundry_group': True
#         }

from collections import defaultdict


# class TrialBalanceLedgerAPIView(APIView):
#     """
#     API endpoint that returns ledger-level trial balance data with full date filtering
#     and open/close functionality. Both the date-range and no-date-range paths produce
#     trial_balance/total in the SAME shape as give_detail() — 'ledger'/'group'/'id' keys,
#     subledgers keyed as 'subledger'/'total_value', debit/credit as '-' when zero — so a
#     single formatter handles both without any key-mismatch risk.
#     """

#     def get(self, request):
#         from_date = request.GET.get('fromDate', None)
#         to_date = request.GET.get('toDate', None)
#         option = request.GET.get('option', None)
#         date_type = request.GET.get('date_type', 'entry_date')
#         show_zero_ledgers = request.GET.get('show_zero_ledgers', 'false').lower() == 'true'

#         org = Organization.objects.first()
#         if not org:
#             return Response(
#                 {"error": "No organization found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         current_fiscal_year = org.current_fiscal_year
#         show_zero = show_zero_ledgers or org.show_zero_ledgers

#         try:
#             if from_date and to_date:
#                 # give_detail() already returns the canonical shape — used whether or not
#                 # option == 'openclose', matching TrialBalanceView's own behavior where
#                 # both its 'openclose' and non-openclose date branches call give_detail.
#                 trial_balance, total = give_detail(from_date, to_date)
#             else:
#                 trial_balance, total = self.get_all_ledgers(show_zero)

#             ledger_data, total = self.format_trial_balance(trial_balance, total)

#             # response_data = {
#             #     'success': True,
#             #     'data': {
#             #         'ledgers': ledger_data,
#             #         'summary': {
#             #             'total_ledgers': len(ledger_data),
#             #             'total_debit': round(total.get('debit_total', 0), 2),
#             #             'total_credit': round(total.get('credit_total', 0), 2),
#             #             'difference': round(total.get('debit_total', 0) - total.get('credit_total', 0), 2),
#             #             'is_balanced': abs(total.get('debit_total', 0) - total.get('credit_total', 0)) < 0.01
#             #         }
#             #     },
#             #     'filters': {
#             #         'from_date': from_date,
#             #         'to_date': to_date,
#             #         'option': option,
#             #         'date_type': date_type,
#             #         'show_zero_ledgers': show_zero,
#             #         'current_fiscal_year': current_fiscal_year
#             #     }
#             # }
#             grouped_ledgers = self.group_ledgers_for_display(ledger_data)

#             response_data = {
#                 'success': True,
#                 'data': {
#                     'ledgers': grouped_ledgers,
#                     'summary': {
#                         'total_ledgers': len(ledger_data),
#                         'total_debit': round(total.get('debit_total', 0), 2),
#                         'total_credit': round(total.get('credit_total', 0), 2),
#                         'difference': round(total.get('debit_total', 0) - total.get('credit_total', 0), 2),
#                         'is_balanced': abs(total.get('debit_total', 0) - total.get('credit_total', 0)) < 0.01
#                     }
#                 },
#                 'filters': {
#                     'from_date': from_date,
#                     'to_date': to_date,
#                     'option': option,
#                     'date_type': date_type,
#                     'show_zero_ledgers': show_zero,
#                     'current_fiscal_year': current_fiscal_year
#                 }
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             return Response(
#                 {
#                     "success": False,
#                     "error": str(e),
#                     "traceback": traceback.format_exc()
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def group_ledgers_for_display(self, ledger_data):
#         """
#         Takes the flat ledger_data list (output of format_trial_balance) and nests it
#         into account_type -> account_group -> ledgers, for easier frontend rendering.
#         Sorted alphabetically by account_type, then account_group, then ledger_name.
#         """
#         grouped = defaultdict(lambda: defaultdict(list))

#         for ledger in ledger_data:
#             account_type = ledger.get('account_type') or 'Uncategorized'
#             account_group = ledger.get('account_group') or 'Uncategorized'

#             if ledger.get('ledger_name') == 'Sundry Debtors':
#                 account_type = 'Asset'
#                 account_group = 'Sundry Debtors'
#             if ledger.get('ledger_name') == 'Sundry Creditors':
#                 account_type = 'Liability'
#                 account_group = 'Sundry Creditors'
#             grouped[account_type][account_group].append(ledger)

#         result = []
#         for account_type in sorted(grouped.keys()):
#             groups = grouped[account_type]
#             group_list = []
#             for account_group in sorted(groups.keys()):
#                 ledgers = sorted(groups[account_group], key=lambda x: x['ledger_name'])
#                 group_list.append({
#                     'account_group': account_group,
#                     'ledgers': ledgers,
#                 })
#             result.append({
#                 'account_type': account_type,
#                 'groups': group_list,
#             })

#         return result

#     def get_all_ledgers(self, show_zero):
#         """
#         No-date-range path. Builds ledger dicts in the SAME shape give_detail() uses
#         ('ledger'/'group'/'id' — not 'ledger_name'/'account_group'/'ledger_id'), so
#         format_trial_balance() below works identically for both paths.
#         """
#         if show_zero:
#             ledgers = AccountLedger.objects.filter(
#                 ~Q(ledger_name='VAT Receivable'),
#                 ~Q(ledger_name='VAT Payable')
#             )
#         else:
#             ledgers = AccountLedger.objects.filter(
#                 ~Q(total_value=0),
#                 ~Q(ledger_name='VAT Receivable'),
#                 ~Q(ledger_name='VAT Payable')
#             )

#         total = {'debit_total': 0, 'credit_total': 0}
#         ledger_dict = {}

#         for led in ledgers:
#             account_type = led.account_chart.account_type
#             account_group = led.account_chart.group

#             if show_zero:
#                 subledgers = AccountSubLedger.objects.filter(ledger_id=led.id)
#             else:
#                 subledgers = AccountSubLedger.objects.filter(ledger_id=led.id, total_value__gt=0.0)

#             subledger_entries = [
#                 {'subledger': sl.sub_ledger_name, 'total_value': sl.total_value, 'subledger_id': sl.id}
#                 for sl in subledgers
#             ]

#             data = {
#                 'account_type': account_type,
#                 'ledger': led.ledger_name,
#                 'group': account_group,
#                 'id': led.id,
#                 'total_value': led.total_value,
#                 'subledgers': subledger_entries,
#             }

#             if account_type in ['Asset', 'Expense']:
#                 if led.total_value > 0:
#                     data['debit'] = led.total_value
#                     data['credit'] = '-'
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['debit_total'] += led.total_value
#                 else:
#                     val = abs(led.total_value)
#                     data['credit'] = val
#                     data['debit'] = '-'
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['credit_total'] += val
#             else:
#                 if led.total_value > 0:
#                     data['credit'] = led.total_value
#                     data['debit'] = '-'
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['credit_total'] += led.total_value
#                 else:
#                     val = abs(led.total_value)
#                     data['debit'] = val
#                     data['credit'] = '-'
#                     if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
#                         total['debit_total'] += val

#             ledger_name = data['ledger']
#             if ledger_name not in ledger_dict:
#                 ledger_dict[ledger_name] = data

#         ledger_list = list(ledger_dict.values())
#         trial_balance = self.group_ledgers_by_account_type(ledger_list)
#         self.handle_vat(trial_balance, total, show_zero)
#         self.handle_sundry(trial_balance, total, show_zero)

#         return trial_balance, total

#     def group_ledgers_by_account_type(self, ledger_list):
#         trial_balance = []
#         for entry in ledger_list:
#             real_account_type = entry['account_type']
#             account_type = entry['group']
#             account_group = entry['group']

#             account_type_entry = next((d for d in trial_balance if d['account_type'] == account_type), None)
#             if not account_type_entry:
#                 trial_balance.append({
#                     'real_account_type': real_account_type,
#                     'account_type': account_type,
#                     'groups': [{'group': account_group, 'ledgers': [entry]}]
#                 })
#             else:
#                 account_group_entry = next((g for g in account_type_entry['groups'] if g['group'] == account_group), None)
#                 if not account_group_entry:
#                     account_type_entry['groups'].append({'group': account_group, 'ledgers': [entry]})
#                 else:
#                     account_group_entry['ledgers'].append(entry)
#         return trial_balance

#     def handle_vat(self, trial_balance, total, show_zero):
#         """Mirrors give_detail's absence of VAT netting — only used on the no-date path,
#         same as before. Uses 'ledger'/'group'/'subledger' keys to match give_detail's shape."""
#         try:
#             vat_receivable = AccountLedger.objects.get(ledger_name='VAT Receivable')
#             vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
#             vat = vat_receivable.total_value - vat_payable.total_value

#             if vat > 0:
#                 subledgers = AccountSubLedger.objects.filter(ledger__ledger_name='VAT Receivable')
#                 subledger_entries = [
#                     {'subledger': sl.sub_ledger_name, 'total_value': sl.total_value, 'subledger_id': sl.id} for sl in subledgers
#                 ]
#                 trial_balance.append({
#                     'real_account_type': vat_receivable.account_chart.account_type,
#                     'account_type': vat_receivable.account_chart.group,
#                     'groups': [{
#                         'group': vat_receivable.account_chart.group,
#                         'ledgers': [{
#                             'ledger': vat_receivable.ledger_name,
#                             'group': vat_receivable.account_chart.account_type,
#                             'id': vat_receivable.id,
#                             'account_type': vat_receivable.account_chart.account_type,
#                             'debit': abs(vat),
#                             'credit': '-',
#                             'total_value': abs(vat),
#                             'subledgers': subledger_entries,
#                         }]
#                     }]
#                 })
#                 total['debit_total'] += abs(vat)
#             elif vat < 0:
#                 subledgers = AccountSubLedger.objects.filter(ledger__ledger_name='VAT Payable')
#                 subledger_entries = [
#                     {'subledger': sl.sub_ledger_name, 'total_value': sl.total_value, 'subledger_id': sl.id} for sl in subledgers
#                 ]
#                 trial_balance.append({
#                     'real_account_type': vat_payable.account_chart.account_type,
#                     'account_type': vat_payable.account_chart.group,
#                     'groups': [{
#                         'group': vat_payable.account_chart.group,
#                         'ledgers': [{
#                             'ledger': vat_payable.ledger_name,
#                             'group': vat_payable.account_chart.account_type,
#                             'id': vat_payable.id,
#                             'account_type': vat_payable.account_chart.account_type,
#                             'debit': '-',
#                             'credit': abs(vat),
#                             'total_value': abs(vat),
#                             'subledgers': subledger_entries,
#                         }]
#                     }]
#                 })
#                 total['credit_total'] += abs(vat)
#         except AccountLedger.DoesNotExist:
#             pass

#     def handle_sundry(self, trial_balance, total, show_zero):
#         """
#         Aggregates Sundry Debtors/Creditors into a single summary row per group,
#         same as give_detail() already does — so this only runs on the no-date path.
#         """
#         debtors_debit = debtors_credit = 0
#         creditors_debit = creditors_credit = 0

#         for entry in trial_balance:
#             for group in entry.get('groups', []):
#                 remaining = []
#                 for ledger in group['ledgers']:
#                     g = ledger.get('group')
#                     debit = ledger.get('debit', 0)
#                     credit = ledger.get('credit', 0)
#                     if g == 'Sundry Debtors':
#                         if debit != '-':
#                             debtors_debit += debit
#                         if credit != '-':
#                             debtors_credit += credit
#                     elif g == 'Sundry Creditors':
#                         if debit != '-':
#                             creditors_debit += debit
#                         if credit != '-':
#                             creditors_credit += credit
#                     else:
#                         remaining.append(ledger)
#                 group['ledgers'] = remaining

#         if debtors_debit != 0 or debtors_credit != 0 or show_zero:
#             value = debtors_debit - debtors_credit
#             debit = value if value >= 0 else '-'
#             credit = '-' if value >= 0 else abs(value)
#             if value >= 0:
#                 total['debit_total'] += value
#             else:
#                 total['credit_total'] += abs(value)

#             ledgers = AccountLedger.objects.filter(account_chart__group="Sundry Debtors")
#             subledger_entries = [{'subledger': l.ledger_name, 'total_value': l.total_value, 'subledger_id': l.id} for l in ledgers]

#             trial_balance.append({
#                 'real_account_type': 'Asset',
#                 'account_type': 'Asset',
#                 'groups': [{
#                     'group': 'Sundry Debtors',
#                     'ledgers': [{
#                         'ledger': 'Sundry Debtors',
#                         'group': 'Sundry Debtors',
#                         'id': None,
#                         'account_type': 'Asset',
#                         'debit': debit,
#                         'credit': credit,
#                         'total_value': abs(value),
#                         'subledgers': subledger_entries,
#                     }]
#                 }]
#             })

#         if creditors_debit != 0 or creditors_credit != 0 or show_zero:
#             value = creditors_credit - creditors_debit
#             credit = value if value >= 0 else '-'
#             debit = '-' if value >= 0 else abs(value)
#             if value >= 0:
#                 total['credit_total'] += value
#             else:
#                 total['debit_total'] += abs(value)

#             ledgers = AccountLedger.objects.filter(account_chart__group="Sundry Creditors")
#             subledger_entries = [{'subledger': l.ledger_name, 'total_value': l.total_value, 'subledger_id': l.id} for l in ledgers]

#             trial_balance.append({
#                 'real_account_type': 'Liability',
#                 'account_type': 'Liability',
#                 'groups': [{
#                     'group': 'Sundry Creditors',
#                     'ledgers': [{
#                         'ledger': 'Sundry Creditors',
#                         'group': 'Sundry Creditors',
#                         'id': None,
#                         'account_type': 'Liability',
#                         'debit': debit,
#                         'credit': credit,
#                         'total_value': abs(value),
#                         'subledgers': subledger_entries,
#                     }]
#                 }]
#             })

#         trial_balance.sort(key=lambda x: x['real_account_type'])

#     def format_trial_balance(self, trial_balance, total):
#         """
#         Single formatter for BOTH paths — safe now because get_all_ledgers() and
#         give_detail() emit identical key shapes ('ledger'/'group'/'id', subledgers
#         keyed 'subledger'/'total_value', debit/credit possibly '-').
#         """
#         all_ledgers = []
#         for entry in trial_balance:
#             for group in entry.get('groups', []):
#                 for ledger in group.get('ledgers', []):
#                     all_ledgers.append(self.format_ledger_for_api(ledger))

#         all_ledgers.sort(key=lambda x: (x['account_type'], x['ledger_name']))
#         return all_ledgers, total

#     # def format_ledger_for_api(self, ledger):
#     #     debit = ledger.get('debit', 0)
#     #     credit = ledger.get('credit', 0)
#     #     debit = 0 if debit == '-' else debit
#     #     credit = 0 if credit == '-' else credit

#     #     subledgers = [
#     #         {
#     #             'subledger_id': sl.get('subledger_id', sl.get('id')),
#     #             'subledger_name': sl.get('subledger_name', sl.get('subledger', '')),
#     #             'total_value': round(sl.get('total_value', 0) or 0, 2),
#     #         }
#     #         for sl in ledger.get('subledgers', [])
#     #     ]

#     #     total_value = ledger.get('total_value', ledger.get('closing', 0)) or 0

#     #     return {
#     #         'ledger_id': ledger.get('id', None),
#     #         'ledger_name': ledger.get('ledger', ''),
#     #         'account_type': ledger.get('account_type', ''),
#     #         'account_group': ledger.get('group', ''),
#     #         'debit': round(debit or 0, 2),
#     #         'credit': round(credit or 0, 2),
#     #         'total_value': round(total_value, 2),
#     #         'subledgers': subledgers,
#     #         'has_subledgers': len(subledgers) > 0,
#     #     }

#     def format_ledger_for_api(self, ledger):
#         debit = ledger.get('debit', 0)
#         credit = ledger.get('credit', 0)
#         debit = 0 if debit == '-' else debit
#         credit = 0 if credit == '-' else credit

#         subledgers = [
#             {
#                 'subledger_id': sl.get('subledger_id', sl.get('id')),
#                 'subledger_name': sl.get('subledger_name', sl.get('subledger', '')),
#                 'total_value': round(sl.get('total_value', 0) or 0, 2),
#             }
#             for sl in ledger.get('subledgers', [])
#         ]

#         total_value = ledger.get('total_value', ledger.get('closing', 0)) or 0
#         opening = ledger.get('opening')
#         closing = ledger.get('closing')

#         return {
#             'ledger_id': ledger.get('id', None),
#             'ledger_name': ledger.get('ledger', ''),
#             'account_type': ledger.get('account_type', ''),
#             'account_group': ledger.get('group', ''),
#             'debit': round(debit or 0, 2),
#             'credit': round(credit or 0, 2),
#             'total_value': round(total_value, 2),
#             'opening': round(opening, 2) if opening is not None else None,
#             'closing': round(closing, 2) if closing is not None else None,
#             'subledgers': subledgers,
#             'has_subledgers': len(subledgers) > 0,
#         }


from accounting.detail_utils import give_detail_expanded_sundry  # add this import

from collections import defaultdict

from accounting.detail_utils import give_detail_expanded_sundry


class TrialBalanceLedgerAPIView(APIView):
    """
    API endpoint that returns ledger-level trial balance data with full date filtering.

    Sundry Debtors / Sundry Creditors are NOT collapsed into a single aggregate
    "control account" row. Each underlying AccountLedger (e.g. individual
    customer/vendor) is treated like any other ledger — its own debit/credit
    (and, on the date-range path, opening/closing) is computed and it's grouped
    normally under account_group 'Sundry Debtors' / 'Sundry Creditors'.

    Both the date-range path (give_detail_expanded_sundry) and the no-date-range
    path (get_all_ledgers) emit the SAME dict shape — 'ledger'/'group'/'id' keys,
    subledgers keyed as 'subledger'/'subledger_id'/'total_value', debit/credit as
    '-' when zero — so a single formatter (format_trial_balance) handles both.
    """

    def get(self, request):
        from_date = request.GET.get('fromDate', None)
        to_date = request.GET.get('toDate', None)
        option = request.GET.get('option', None)
        date_type = request.GET.get('date_type', 'entry_date')
        show_zero_ledgers = request.GET.get('show_zero_ledgers', 'false').lower() == 'true'

        org = Organization.objects.first()
        if not org:
            return Response(
                {"error": "No organization found"},
                status=status.HTTP_404_NOT_FOUND
            )

        current_fiscal_year = org.current_fiscal_year
        show_zero = show_zero_ledgers or org.show_zero_ledgers

        try:
            if from_date and to_date:
                trial_balance, total = give_detail_expanded_sundry(from_date, to_date)
            else:
                trial_balance, total = self.get_all_ledgers(show_zero)

            ledger_data, total = self.format_trial_balance(trial_balance, total)
            grouped_ledgers = self.group_ledgers_for_display(ledger_data)

            response_data = {
                'success': True,
                'data': {
                    'ledgers': grouped_ledgers,
                    'summary': {
                        'total_ledgers': len(ledger_data),
                        'total_debit': round(total.get('debit_total', 0), 2),
                        'total_credit': round(total.get('credit_total', 0), 2),
                        'difference': round(total.get('debit_total', 0) - total.get('credit_total', 0), 2),
                        'is_balanced': abs(total.get('debit_total', 0) - total.get('credit_total', 0)) < 0.01
                    }
                },
                'filters': {
                    'from_date': from_date,
                    'to_date': to_date,
                    'option': option,
                    'date_type': date_type,
                    'show_zero_ledgers': show_zero,
                    'current_fiscal_year': current_fiscal_year
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def group_ledgers_for_display(self, ledger_data):
        """
        Nests the flat ledger_data list into account_type -> account_group -> ledgers,
        sorted alphabetically at every level. Sundry Debtors/Creditors ledgers now
        carry their own correct account_type/account_group already (they come through
        as normal ledgers), so no special-casing is needed here.
        """
        grouped = defaultdict(lambda: defaultdict(list))

        for ledger in ledger_data:
            account_type = ledger.get('account_type') or 'Uncategorized'
            account_group = ledger.get('account_group') or 'Uncategorized'
            grouped[account_type][account_group].append(ledger)

        result = []
        for account_type in sorted(grouped.keys()):
            groups = grouped[account_type]
            group_list = []
            for account_group in sorted(groups.keys()):
                ledgers = sorted(groups[account_group], key=lambda x: x['ledger_name'])
                group_list.append({
                    'account_group': account_group,
                    'ledgers': ledgers,
                })
            result.append({
                'account_type': account_type,
                'groups': group_list,
            })

        return result

    def get_all_ledgers(self, show_zero):
        """
        No-date-range path. Builds ledger dicts in the SAME shape
        give_detail_expanded_sundry() uses. Sundry Debtors/Creditors ledgers are
        NOT excluded from totals or pulled into a separate aggregate row — they
        flow through like any other ledger, grouped by their real account_group.
        """
        if show_zero:
            ledgers = AccountLedger.objects.filter(
                ~Q(ledger_name='VAT Receivable'),
                ~Q(ledger_name='VAT Payable')
            )
        else:
            ledgers = AccountLedger.objects.filter(
                ~Q(total_value=0),
                ~Q(ledger_name='VAT Receivable'),
                ~Q(ledger_name='VAT Payable')
            )

        total = {'debit_total': 0, 'credit_total': 0}
        ledger_dict = {}

        for led in ledgers:
            account_type = led.account_chart.account_type
            account_group = led.account_chart.group

            if show_zero:
                subledgers = AccountSubLedger.objects.filter(ledger_id=led.id)
            else:
                subledgers = AccountSubLedger.objects.filter(ledger_id=led.id, total_value__gt=0.0)

            subledger_entries = [
                {'subledger': sl.sub_ledger_name, 'total_value': sl.total_value, 'subledger_id': sl.id}
                for sl in subledgers
            ]

            data = {
                'account_type': account_type,
                'ledger': led.ledger_name,
                'group': account_group,
                'id': led.id,
                'total_value': led.total_value,
                'subledgers': subledger_entries,
            }

            if account_type in ['Asset', 'Expense']:
                if led.total_value > 0:
                    data['debit'] = led.total_value
                    data['credit'] = '-'
                    total['debit_total'] += led.total_value
                else:
                    val = abs(led.total_value)
                    data['credit'] = val
                    data['debit'] = '-'
                    total['credit_total'] += val
            else:
                if led.total_value > 0:
                    data['credit'] = led.total_value
                    data['debit'] = '-'
                    total['credit_total'] += led.total_value
                else:
                    val = abs(led.total_value)
                    data['debit'] = val
                    data['credit'] = '-'
                    total['debit_total'] += val

            ledger_name = data['ledger']
            if ledger_name not in ledger_dict:
                ledger_dict[ledger_name] = data

        ledger_list = list(ledger_dict.values())
        trial_balance = self.group_ledgers_by_account_type(ledger_list)
        self.handle_vat(trial_balance, total, show_zero)

        return trial_balance, total

    def group_ledgers_by_account_type(self, ledger_list):
        trial_balance = []
        for entry in ledger_list:
            real_account_type = entry['account_type']
            account_type = entry['group']
            account_group = entry['group']

            account_type_entry = next((d for d in trial_balance if d['account_type'] == account_type), None)
            if not account_type_entry:
                trial_balance.append({
                    'real_account_type': real_account_type,
                    'account_type': account_type,
                    'groups': [{'group': account_group, 'ledgers': [entry]}]
                })
            else:
                account_group_entry = next((g for g in account_type_entry['groups'] if g['group'] == account_group), None)
                if not account_group_entry:
                    account_type_entry['groups'].append({'group': account_group, 'ledgers': [entry]})
                else:
                    account_group_entry['ledgers'].append(entry)
        return trial_balance

    def handle_vat(self, trial_balance, total, show_zero):
        """
        Nets VAT Receivable/Payable into a single row — only used on the
        no-date-range path (give_detail_expanded_sundry doesn't do VAT netting).
        Uses 'ledger'/'group'/'subledger' keys to match the canonical shape.
        """
        try:
            vat_receivable = AccountLedger.objects.get(ledger_name='VAT Receivable')
            vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
            vat = vat_receivable.total_value - vat_payable.total_value

            if vat > 0:
                subledgers = AccountSubLedger.objects.filter(ledger__ledger_name='VAT Receivable')
                subledger_entries = [
                    {'subledger': sl.sub_ledger_name, 'total_value': sl.total_value, 'subledger_id': sl.id}
                    for sl in subledgers
                ]
                trial_balance.append({
                    'real_account_type': vat_receivable.account_chart.account_type,
                    'account_type': vat_receivable.account_chart.group,
                    'groups': [{
                        'group': vat_receivable.account_chart.group,
                        'ledgers': [{
                            'ledger': vat_receivable.ledger_name,
                            'group': vat_receivable.account_chart.account_type,
                            'id': vat_receivable.id,
                            'account_type': vat_receivable.account_chart.account_type,
                            'debit': abs(vat),
                            'credit': '-',
                            'total_value': abs(vat),
                            'subledgers': subledger_entries,
                        }]
                    }]
                })
                total['debit_total'] += abs(vat)
            elif vat < 0:
                subledgers = AccountSubLedger.objects.filter(ledger__ledger_name='VAT Payable')
                subledger_entries = [
                    {'subledger': sl.sub_ledger_name, 'total_value': sl.total_value, 'subledger_id': sl.id}
                    for sl in subledgers
                ]
                trial_balance.append({
                    'real_account_type': vat_payable.account_chart.account_type,
                    'account_type': vat_payable.account_chart.group,
                    'groups': [{
                        'group': vat_payable.account_chart.group,
                        'ledgers': [{
                            'ledger': vat_payable.ledger_name,
                            'group': vat_payable.account_chart.account_type,
                            'id': vat_payable.id,
                            'account_type': vat_payable.account_chart.account_type,
                            'debit': '-',
                            'credit': abs(vat),
                            'total_value': abs(vat),
                            'subledgers': subledger_entries,
                        }]
                    }]
                })
                total['credit_total'] += abs(vat)
        except AccountLedger.DoesNotExist:
            pass

    def format_trial_balance(self, trial_balance, total):
        """
        Single formatter for BOTH paths — safe because get_all_ledgers() and
        give_detail_expanded_sundry() emit identical key shapes.
        """
        all_ledgers = []
        for entry in trial_balance:
            for group in entry.get('groups', []):
                for ledger in group.get('ledgers', []):
                    all_ledgers.append(self.format_ledger_for_api(ledger))

        all_ledgers.sort(key=lambda x: (x['account_type'], x['ledger_name']))
        return all_ledgers, total

    def format_ledger_for_api(self, ledger):
        debit = ledger.get('debit', 0)
        credit = ledger.get('credit', 0)
        debit = 0 if debit == '-' else debit
        credit = 0 if credit == '-' else credit

        subledgers = [
            {
                'subledger_id': sl.get('subledger_id', sl.get('id')),
                'subledger_name': sl.get('subledger_name', sl.get('subledger', '')),
                'total_value': round(sl.get('total_value', 0) or 0, 2),
            }
            for sl in ledger.get('subledgers', [])
        ]

        total_value = ledger.get('total_value', ledger.get('closing', 0)) or 0
        opening = ledger.get('opening')
        closing = ledger.get('closing')

        return {
            'ledger_id': ledger.get('id', None),
            'ledger_name': ledger.get('ledger', ''),
            'account_type': ledger.get('account_type', ''),
            'account_group': ledger.get('group', ''),
            'debit': round(debit or 0, 2),
            'credit': round(credit or 0, 2),
            'total_value': round(total_value, 2),
            'opening': round(opening, 2) if opening is not None else None,
            'closing': round(closing, 2) if closing is not None else None,
            'subledgers': subledgers,
            'has_subledgers': len(subledgers) > 0,
        }

from decimal import Decimal
from itertools import chain

from django.db.models import Sum, Min


from accounting.models import (
    AccountLedger,
    TblCrJournalEntry,
    TblDrJournalEntry
)


def _decimal_to_str(value):
    """Serialize Decimal safely for JSON (avoids float precision issues)."""
    if isinstance(value, Decimal):
        return str(value)
    return value


from accounting.utils import build_subledgers_cashflow_batch
class LedgerDetailAPIView(APIView):

    def get(self, request, ledger_id):
        ledger = get_object_or_404(AccountLedger, id=ledger_id)
        current_date = datetime.today().date()

        credit_entries = TblCrJournalEntry.objects.filter(ledger=ledger)
        debit_entries = TblDrJournalEntry.objects.filter(ledger=ledger)

        total_credit = Decimal('0')
        total_debit = Decimal('0')

        from_date = request.GET.get('fromDate')
        to_date = request.GET.get('toDate')
        option = request.GET.get('option')
        current_fiscal_year = Organization.objects.last().current_fiscal_year

        if from_date and to_date:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            credit_entries = TblCrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__entry_date__range=[from_date, to_date_obj]
            )
            debit_entries = TblDrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__entry_date__range=[from_date, to_date_obj]
            )

        else:
            # Return error response when date range is missing
            return Response(
                {"error": "No date range provided. Please provide both fromDate and toDate parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subledgers = list(
                    AccountSubLedger.objects.filter(ledger=ledger).select_related(
                        'ledger__account_chart'
                    )
                )
        subledgers_by_id = build_subledgers_cashflow_batch(subledgers, from_date, to_date)
        subledgers_data = list(subledgers_by_id.values())

        unique_journal_ids_cr = credit_entries.values_list('journal_entry_id', flat=True).distinct()
        unique_journal_ids_dr = debit_entries.values_list('journal_entry_id', flat=True).distinct()

        details = []

        for journal_id in unique_journal_ids_cr:
            dr_entries = TblDrJournalEntry.objects.filter(journal_entry_id=journal_id)
            cr_entries = TblCrJournalEntry.objects.filter(journal_entry_id=journal_id, ledger_id=ledger.id)

            ledger_names = [entry.ledger.ledger_name for entry in dr_entries]
            ledger_amounts = [entry.debit_amount for entry in dr_entries]
            payers_info = ', '.join([f'{name} ({amount})' for name, amount in zip(ledger_names, ledger_amounts)])

            for entry in cr_entries:
                details.append({
                    'journal_id': journal_id,
                    'payers': payers_info,
                    'date': entry.journal_entry.entry_date.strftime('%Y-%m-%d'),
                    'particulars': entry.particulars,
                    'debit': '0',
                    'credit': _decimal_to_str(entry.credit_amount),
                })

        for journal_id in unique_journal_ids_dr:
            cr_entries = TblCrJournalEntry.objects.filter(journal_entry_id=journal_id)
            dr_entries = TblDrJournalEntry.objects.filter(journal_entry_id=journal_id, ledger_id=ledger.id)

            ledger_names = [entry.ledger.ledger_name for entry in cr_entries]
            ledger_amounts = [entry.credit_amount for entry in cr_entries]
            payers_info = ', '.join([f'{name} ({amount})' for name, amount in zip(ledger_names, ledger_amounts)])

            for entry in dr_entries:
                details.append({
                    'journal_id': journal_id,
                    'payers': payers_info,
                    'date': entry.journal_entry.entry_date.strftime('%Y-%m-%d'),
                    'particulars': entry.particulars,
                    'debit': _decimal_to_str(entry.debit_amount),
                    'credit': '0',
                })

        sorted_details = sorted(details, key=lambda x: x['date'])

        all_dates = list(credit_entries.values_list('journal_entry__entry_date', flat=True)) + \
                    list(debit_entries.values_list('journal_entry__entry_date', flat=True))

        if all_dates:
            first_date = min(all_dates)
            last_date = max(all_dates)
        else:
            first_date = last_date = None

        for entry in credit_entries:
            total_credit += entry.credit_amount
        for entry in debit_entries:
            total_debit += entry.debit_amount

        all_entries_qs = sorted(
            chain(credit_entries, debit_entries),
            key=lambda x: x.journal_entry.entry_date
        )

        # Serialize the mixed cr/dr queryset into a flat, JSON-friendly list
        serialized_entries = []
        for entry in all_entries_qs:
            is_credit = isinstance(entry, TblCrJournalEntry)
            serialized_entries.append({
                'journal_entry_id': entry.journal_entry_id,
                'date': entry.journal_entry.entry_date.strftime('%Y-%m-%d'),
                'particulars': entry.particulars,
                'credit': _decimal_to_str(entry.credit_amount) if is_credit else '0',
                'debit': _decimal_to_str(entry.debit_amount) if not is_credit else '0',
            })

        total_diff = total_debit - total_credit
        closing_balance = abs(total_diff)
        neg = 1 if total_diff < 0 else 2 if total_diff == 0 else 0

        # Opening Balance
        earliest_credit_date = TblCrJournalEntry.objects.aggregate(
            earliest_credit_date=Min('journal_entry__entry_date')
        )['earliest_credit_date'] or current_date
        earliest_debit_date = TblDrJournalEntry.objects.aggregate(
            earliest_debit_date=Min('journal_entry__entry_date')
        )['earliest_debit_date'] or current_date
        first_date1 = min(earliest_credit_date, earliest_debit_date)

        opening_credit_entries = TblCrJournalEntry.objects.filter(
            ledger=ledger,
            journal_entry__entry_date__range=[first_date1, current_date]
        )
        opening_balance_credit = opening_credit_entries.aggregate(
            total_credit=Sum('credit_amount')
        )['total_credit'] or 0

        opening_debit_entries = TblDrJournalEntry.objects.filter(
            ledger=ledger,
            journal_entry__entry_date__range=[first_date1, current_date]
        )
        opening_balance_debit = opening_debit_entries.aggregate(
            total_debit=Sum('debit_amount')
        )['total_debit'] or 0

        if option == 'openclose':
            if total_diff < 0:
                opening_balance_credit = abs(total_diff)
            else:
                closing_balance = total_diff

        if from_date:
            opening_balance_credit = TblCrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__entry_date__lt=from_date
            ).aggregate(total=Sum('credit_amount'))['total'] or 0

            opening_balance_debit = TblDrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__entry_date__lt=from_date
            ).aggregate(total=Sum('debit_amount'))['total'] or 0

            to_date = datetime.strptime(to_date, '%Y-%m-%d').strftime('%Y-%m-%d')

        data = {
            'ledger': {
                'id': ledger.id,
                'name': getattr(ledger, 'ledger_name', None),
            },
            # 'entries': serialized_entries,
            'total_debit': _decimal_to_str(total_debit),
            'total_credit': _decimal_to_str(total_credit),
            'closing_balance': _decimal_to_str(closing_balance),
            'opening_balance': {
                'credit': _decimal_to_str(opening_balance_credit),
                'debit': _decimal_to_str(opening_balance_debit),
            },
            'from_date': from_date,
            'to_date': to_date,
            'openclose': option == 'openclose',
            'neg': neg,
            'current_fiscal_year': str(current_fiscal_year) if current_fiscal_year is not None else None,
            'first_credit_date': first_date.strftime('%Y-%m-%d') if first_date else None,
            'last_credit_date': last_date.strftime('%Y-%m-%d') if last_date else None,
            'sorted_details': sorted_details,
            'subledgers': subledgers_data
        }
        return Response(data, status=status.HTTP_200_OK)


class SubLedgerCashflowAPIView(APIView):
    def get(self, request):
        subledger_id = request.GET.get('subledger_id')
        from_date = request.GET.get('fromDate')
        to_date = request.GET.get('toDate')

        if not subledger_id:
            return Response({'error': 'subledger_id is required'}, status=400)

        subledger = get_object_or_404(
            AccountSubLedger.objects.select_related('ledger__account_chart'),
            id=subledger_id
        )
        result = build_subledgers_cashflow_batch([subledger], from_date, to_date)
        return Response(result[subledger.id])
    