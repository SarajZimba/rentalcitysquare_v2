from organization.models import Organization
from accounting.models import AccountLedger, AccountSubLedger, CumulativeLedger, AccountSubLedgerTracking
from django.db.models import Q, Sum
from django.shortcuts import render
from datetime import datetime, timedelta

from django.db.models import Sum, F
from django.utils.dateparse import parse_datetime

# def get_subledger_data(from_date, to_date, subledgers):
#     subledger_ids = subledgers.values_list('id', flat=True)
#     # Ensure dates are properly formatted
#     # from_date = parse_datetime(from_date)
#     # to_date = parse_datetime(to_date)

#     # Filter AccountSubLedgerTracking entries by date range
#     subledger_entries = []
#     # for subledger in subledgers:
#         # tracking_entries = AccountSubLedgerTracking.objects.filter(
#         #     created_at__range=(from_date, to_date), subledger=subledger
#         # )

#         # # Aggregate the total value_changed for each subledger
#         # aggregated_data = tracking_entries.values('subledger').annotate(
#         #     total_value_changed=Sum('value_changed')
#         # )
#     aggregated_data = (
#         AccountSubLedgerTracking.objects
#         .filter(
#             created_at__range=(from_date, to_date),
#             subledger__in=subledger_ids  # Filter by the IDs of the provided subledgers
#         )
#         .values('subledger__sub_ledger_name')  # Group by subledger name
#         .annotate(
#             total_value=Sum('value_changed')  # Aggregate value_changed
#         )
#     )

#     print(aggregated_data)
#     for data in aggregated_data:
#          subledger_dict = {
#               "subledger": data['subledger__sub_ledger_name'],
#               "total_value": data['total_value']
#          }

#          subledger_entries.append(subledger_dict)
#     print(f'subledger_entries {subledger_entries}')

#     return subledger_entries


def get_subledger_data(from_date, to_date, subledgers):
    subledger_ids = subledgers.values_list('id', flat=True)

    aggregated_data = (
        AccountSubLedgerTracking.objects
        .filter(
            journal__entry_date__range=(from_date, to_date),
            subledger__in=subledger_ids
        )
        .values('subledger__id', 'subledger__sub_ledger_name')
        .annotate(
            total_value=Sum('value_changed')
        )
    )

    subledger_entries = []
    for data in aggregated_data:
        subledger_dict = {
            "subledger": data['subledger__sub_ledger_name'],
            "total_value": data['total_value'],
            "subledger_id": data['subledger__id'],
        }
        subledger_entries.append(subledger_dict)

    return subledger_entries

from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Q, Sum

def give_detail(from_date, to_date, group=None):
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
    # to_date = datetime.strptime(to_date, '%Y-%m-%d') 

    org = Organization.objects.last()
    current_fiscal_year = org.current_fiscal_year
    show_zero_ledgers = org.show_zero_ledgers

    # Fetch all AccountLedgers once
    all_ledgers = AccountLedger.objects.select_related('account_chart').all()

    if group is not None:
        all_ledgers = all_ledgers.filter(account_chart=group)

    # Pre-fetch all required ledger IDs
    all_ledger_ids = [l.id for l in all_ledgers]

    # Pre-fetch before and within transactions
    before_transactions = CumulativeLedger.objects.filter(entry_date__lt=from_date, ledger_id__in=all_ledger_ids)
    filtered_transactions = CumulativeLedger.objects.filter(
        Q(entry_date__range=[from_date, to_date]),
        Q(debit_amount__gt=0) | Q(credit_amount__gt=0),
        ledger_id__in=all_ledger_ids
    )

    # Aggregate filtered transactions
    filtered_sum = filtered_transactions.values(
        'ledger_name', 'account_chart__account_type', 'account_chart__group', 'ledger'
    ).annotate(
        debit=Sum('debit_amount'),
        credit=Sum('credit_amount')
    )

    # Map: ledger_name -> opening balance
    opening_balances = defaultdict(lambda: 0)

    before_sums = before_transactions.values('ledger_name', 'account_chart__account_type').annotate(
        total_debit=Sum('debit_amount'),
        total_credit=Sum('credit_amount')
    )

    for item in before_sums:
        key = item['ledger_name']
        acc_type = item['account_chart__account_type']
        if acc_type in ['Asset', 'Expense']:
            opening_balances[key] = (item['total_debit'] or 0) - (item['total_credit'] or 0)
        else:
            opening_balances[key] = (item['total_credit'] or 0) - (item['total_debit'] or 0)

    # ledger_dict will hold all ledger entries
    ledger_dict = {}
    total = {'debit_total': 0, 'credit_total': 0}

    for led in filtered_sum:
        name = led['ledger_name']
        acc_type = led['account_chart__account_type']
        group = led['account_chart__group']
        id_ = led['ledger']
        debit = led['debit'] or 0
        credit = led['credit'] or 0
        opening = opening_balances.get(name, 0)

        # Subledgers
        subledger_filter = Q(ledger_id=id_)
        if not show_zero_ledgers:
            subledger_filter &= Q(total_value__gt=0.0)
        subledgers = AccountSubLedger.objects.filter(subledger_filter)
        subledger_entries = get_subledger_data(from_date, to_date, subledgers)

        data = {
            'account_type': acc_type,
            'ledger': name,
            'group': group,
            'id': id_,
            'opening': opening,
            'subledgers': subledger_entries,
            'debit': debit,
            'credit': credit
        }

        # Handle total and closing
        if group not in ["Sundry Debtors", "Sundry Creditors"]:
            if acc_type in ['Asset', 'Expense']:
                total['debit_total'] += debit
                total['credit_total'] += credit
                data['closing'] = opening + debit - credit
            else:
                total['debit_total'] += debit
                total['credit_total'] += credit
                data['closing'] = opening + credit - debit
        else:
            # defer closing, aggregate separately
            pass

        ledger_dict[name] = data

    # Add any missing ledgers not in filtered_sum
    for ledger in all_ledgers:
        if ledger.ledger_name in ledger_dict:
            continue

        name = ledger.ledger_name
        acc_type = ledger.account_chart.account_type
        group = ledger.account_chart.group
        id_ = ledger.id
        opening = opening_balances.get(name, 0)

        # Only if it has value
        if CumulativeLedger.objects.filter(ledger_id=id_, total_value__gt=0).exists():
            subledger_filter = Q(ledger_id=id_)
            if not show_zero_ledgers:
                subledger_filter &= Q(total_value__gt=0.0)
            subledgers = AccountSubLedger.objects.filter(subledger_filter)
            subledger_entries = get_subledger_data(from_date, to_date, subledgers)

            ledger_dict[name] = {
                'account_type': acc_type,
                'ledger': name,
                'group': group,
                'id': id_,
                'opening': opening,
                'subledgers': subledger_entries,
                'debit': 0,
                'credit': 0,
                'closing': opening
            }

    # Trial balance structure
    trial_balance_map = defaultdict(lambda: defaultdict(list))

    Sundry_debtors_debit_total = 0
    Sundry_debtors_credit_total = 0
    Sundry_creditors_debit_total = 0
    Sundry_creditors_credit_total = 0

    for data in ledger_dict.values():
        group = data['group']
        if group == 'Sundry Debtors':
            Sundry_debtors_debit_total += data['debit']
            Sundry_debtors_credit_total += data['credit']
            continue
        if group == 'Sundry Creditors':
            Sundry_creditors_debit_total += data['debit']
            Sundry_creditors_credit_total += data['credit']
            continue

        trial_balance_map[data['account_type']][group].append(data)

    trial_balance = []
    for acc_type, groups in trial_balance_map.items():
        group_list = [{'group': grp, 'ledgers': ledgers} for grp, ledgers in groups.items()]
        trial_balance.append({'real_account_type': acc_type, 'account_type': acc_type, 'groups': group_list})

    # Handle Sundry Debtors
    if Sundry_debtors_debit_total != 0 or Sundry_debtors_credit_total != 0:
        value = Sundry_debtors_debit_total - Sundry_debtors_credit_total
        if value >= 0:
            debit = value
            credit = "-"
            total['debit_total'] += value
        else:
            credit = abs(value)
            debit = "-"
            total['credit_total'] += abs(value)

        subledgers = AccountLedger.objects.filter(account_chart__group="Sundry Debtors")
        subledger_entries = [{'subledger': l.ledger_name, 'total_value': l.total_value, 'subledger_id': l.id} for l in subledgers]

        trial_balance.append({
            'real_account_type': 'Asset',
            'account_type': 'Asset',
            'groups': [{
                'group': 'Sundry Debtors',
                'ledgers': [{
                    'ledger': 'Sundry Debtors',
                    'group': 'Asset',
                    'debit': debit,
                    'credit': credit,
                    'subledgers': subledger_entries
                }]
            }]
        })

    # Handle Sundry Creditors
    if Sundry_creditors_debit_total != 0 or Sundry_creditors_credit_total != 0:
        value = Sundry_creditors_credit_total - Sundry_creditors_debit_total
        if value >= 0:
            credit = value
            debit = "-"
            total['credit_total'] += value
        else:
            debit = abs(value)
            credit = "-"
            total['debit_total'] += abs(value)

        subledgers = AccountLedger.objects.filter(account_chart__group="Sundry Creditors")
        subledger_entries = [{'subledger': l.ledger_name, 'total_value': l.total_value,  'subledger_id': l.id} for l in subledgers]

        trial_balance.append({
            'real_account_type': 'Liability',
            'account_type': 'Liability',
            'groups': [{
                'group': 'Sundry Creditors',
                'ledgers': [{
                    'ledger': 'Sundry Creditors',
                    'group': 'Liability',
                    'debit': debit,
                    'credit': credit,
                    'subledgers': subledger_entries
                }]
            }]
        })

    trial_balance.sort(key=lambda x: x['real_account_type'])

    return trial_balance, total

# from collections import defaultdict
# from datetime import datetime, timedelta
# from django.db.models import Q, Sum

# def give_detail(from_date, to_date, group=None):
#     from_date = datetime.strptime(from_date, '%Y-%m-%d')
#     to_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
#     # to_date = datetime.strptime(to_date, '%Y-%m-%d') 

#     org = Organization.objects.last()
#     current_fiscal_year = org.current_fiscal_year
#     show_zero_ledgers = org.show_zero_ledgers

#     # Fetch all AccountLedgers once
#     all_ledgers = AccountLedger.objects.select_related('account_chart').all()

#     if group is not None:
#         all_ledgers = all_ledgers.filter(account_chart=group)

#     # Pre-fetch all required ledger IDs
#     all_ledger_ids = [l.id for l in all_ledgers]

#     # Pre-fetch before and within transactions
#     before_transactions = CumulativeLedger.objects.filter(entry_date__lt=from_date, ledger_id__in=all_ledger_ids)
#     filtered_transactions = CumulativeLedger.objects.filter(
#         Q(entry_date__range=[from_date, to_date]),
#         Q(debit_amount__gt=0) | Q(credit_amount__gt=0),
#         ledger_id__in=all_ledger_ids
#     )

#     # Aggregate filtered transactions
#     filtered_sum = filtered_transactions.values(
#         'ledger_name', 'account_chart__account_type', 'account_chart__group', 'ledger'
#     ).annotate(
#         debit=Sum('debit_amount'),
#         credit=Sum('credit_amount')
#     )

#     # Map: ledger_name -> opening balance
#     opening_balances = defaultdict(lambda: 0)

#     before_sums = before_transactions.values('ledger_name', 'account_chart__account_type').annotate(
#         total_debit=Sum('debit_amount'),
#         total_credit=Sum('credit_amount')
#     )

#     for item in before_sums:
#         key = item['ledger_name']
#         acc_type = item['account_chart__account_type']
#         if acc_type in ['Asset', 'Expense']:
#             opening_balances[key] = (item['total_debit'] or 0) - (item['total_credit'] or 0)
#         else:
#             opening_balances[key] = (item['total_credit'] or 0) - (item['total_debit'] or 0)

#     # ledger_dict will hold all ledger entries
#     ledger_dict = {}
#     total = {'debit_total': 0, 'credit_total': 0}

#     for led in filtered_sum:
#         name = led['ledger_name']
#         acc_type = led['account_chart__account_type']
#         group = led['account_chart__group']
#         id_ = led['ledger']
#         debit = led['debit'] or 0
#         credit = led['credit'] or 0
#         opening = opening_balances.get(name, 0)

#         # Subledgers
#         subledger_filter = Q(ledger_id=id_)
#         if not show_zero_ledgers:
#             subledger_filter &= Q(total_value__gt=0.0)
#         subledgers = AccountSubLedger.objects.filter(subledger_filter)
#         subledger_entries = get_subledger_data(from_date, to_date, subledgers)

#         data = {
#             'account_type': acc_type,
#             'ledger': name,
#             'group': group,
#             'id': id_,
#             'opening': opening,
#             'subledgers': subledger_entries,
#             'debit': debit,
#             'credit': credit
#         }

#         # Handle total and closing
#         if group not in ["Sundry Debtors", "Sundry Creditors"]:
#             if acc_type in ['Asset', 'Expense']:
#                 total['debit_total'] += debit
#                 total['credit_total'] += credit
#                 data['closing'] = opening + debit - credit
#             else:
#                 total['debit_total'] += debit
#                 total['credit_total'] += credit
#                 data['closing'] = opening + credit - debit
#         else:
#             # defer closing, aggregate separately
#             pass

#         ledger_dict[name] = data

#     # Add any missing ledgers not in filtered_sum
#     for ledger in all_ledgers:
#         if ledger.ledger_name in ledger_dict:
#             continue

#         name = ledger.ledger_name
#         acc_type = ledger.account_chart.account_type
#         group = ledger.account_chart.group
#         id_ = ledger.id
#         opening = opening_balances.get(name, 0)

#         # Only if it has value
#         if CumulativeLedger.objects.filter(ledger_id=id_, total_value__gt=0).exists():
#             subledger_filter = Q(ledger_id=id_)
#             if not show_zero_ledgers:
#                 subledger_filter &= Q(total_value__gt=0.0)
#             subledgers = AccountSubLedger.objects.filter(subledger_filter)
#             subledger_entries = get_subledger_data(from_date, to_date, subledgers)

#             ledger_dict[name] = {
#                 'account_type': acc_type,
#                 'ledger': name,
#                 'group': group,
#                 'id': id_,
#                 'opening': opening,
#                 'subledgers': subledger_entries,
#                 'debit': 0,
#                 'credit': 0,
#                 'closing': opening
#             }

#     # Trial balance structure
#     trial_balance_map = defaultdict(lambda: defaultdict(list))

#     Sundry_debtors_debit_total = 0
#     Sundry_debtors_credit_total = 0
#     Sundry_creditors_debit_total = 0
#     Sundry_creditors_credit_total = 0

#     for data in ledger_dict.values():
#         group = data['group']
#         if group == 'Sundry Debtors':
#             Sundry_debtors_debit_total += data['debit']
#             Sundry_debtors_credit_total += data['credit']
#             continue
#         if group == 'Sundry Creditors':
#             Sundry_creditors_debit_total += data['debit']
#             Sundry_creditors_credit_total += data['credit']
#             continue

#         trial_balance_map[data['account_type']][group].append(data)

#     trial_balance = []
#     for acc_type, groups in trial_balance_map.items():
#         group_list = [{'group': grp, 'ledgers': ledgers} for grp, ledgers in groups.items()]
#         trial_balance.append({'real_account_type': acc_type, 'account_type': acc_type, 'groups': group_list})

#     # Handle Sundry Debtors
#     if Sundry_debtors_debit_total != 0 or Sundry_debtors_credit_total != 0:
#         value = Sundry_debtors_debit_total - Sundry_debtors_credit_total
#         if value >= 0:
#             debit = value
#             credit = "-"
#             total['debit_total'] += value
#         else:
#             credit = abs(value)
#             debit = "-"
#             total['credit_total'] += abs(value)

#         subledgers = AccountLedger.objects.filter(account_chart__group="Sundry Debtors")
#         subledger_entries = [{'subledger': l.ledger_name, 'total_value': l.total_value} for l in subledgers]

#         trial_balance.append({
#             'real_account_type': 'Asset',
#             'account_type': 'Asset',
#             'groups': [{
#                 'group': 'Sundry Debtors',
#                 'ledgers': [{
#                     'ledger': 'Sundry Debtors',
#                     'group': 'Asset',
#                     'debit': debit,
#                     'credit': credit,
#                     'subledgers': subledger_entries
#                 }]
#             }]
#         })

#     # Handle Sundry Creditors
#     if Sundry_creditors_debit_total != 0 or Sundry_creditors_credit_total != 0:
#         value = Sundry_creditors_credit_total - Sundry_creditors_debit_total
#         if value >= 0:
#             credit = value
#             debit = "-"
#             total['credit_total'] += value
#         else:
#             debit = abs(value)
#             credit = "-"
#             total['debit_total'] += abs(value)

#         subledgers = AccountLedger.objects.filter(account_chart__group="Sundry Creditors")
#         subledger_entries = [{'subledger': l.ledger_name, 'total_value': l.total_value} for l in subledgers]

#         trial_balance.append({
#             'real_account_type': 'Liability',
#             'account_type': 'Liability',
#             'groups': [{
#                 'group': 'Sundry Creditors',
#                 'ledgers': [{
#                     'ledger': 'Sundry Creditors',
#                     'group': 'Liability',
#                     'debit': debit,
#                     'credit': credit,
#                     'subledgers': subledger_entries
#                 }]
#             }]
#         })

#     trial_balance.sort(key=lambda x: x['real_account_type'])

#     return trial_balance, total
        
def get_standard_trial_balance():
        

    trial_balance = []
    total = {'debit_total': 0, 'credit_total': 0}
    ledgers = AccountLedger.objects.filter(~Q(total_value=0), ~Q(ledger_name='VAT Receivable'), ~Q(ledger_name='VAT Payable'))
                # ledgers = AccountLedger.objects.filter(~Q(total_value=0))

                # Create a dictionary to store ledger entries based on their names
    ledger_dict = {}

    for led in ledgers:
        data = {}
        account_type = led.account_chart.account_type
        account_group = led.account_chart.group
        data['account_type'] = account_type
        data['ledger'] = led.ledger_name
        data['group'] = account_group  # Use account_group here
        data['id'] = led.id

        if Organization.objects.first().show_zero_ledgers:
            subledgers = AccountSubLedger.objects.filter(ledger_id = led.id)
        else:
            subledgers = AccountSubLedger.objects.filter(ledger_id = led.id, total_value__gt=0.0)
                    # subledgers = AccountSubLedger.objects.filter(ledger_id = led.id)
    
        subledger_entries = []

        for subledger in subledgers:
            subledger_data = {
                'subledger': subledger.sub_ledger_name,
                'total_value': subledger.total_value
            }
            subledger_entries.append(subledger_data)
        data['subledgers'] = subledger_entries
        if account_type in ['Asset', 'Expense']:
            if led.total_value > 0:
                data['debit'] = led.total_value
                if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
                    total['debit_total'] += led.total_value
                data['credit'] = '-'
            else:
                val = abs(led.total_value)
                data['credit'] = val
                if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
                    total['credit_total'] += val
                data['debit'] = '-'
        else:
            if led.total_value > 0:
                data['credit'] = led.total_value
                if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
                    total['credit_total'] += led.total_value
                data['debit'] = '-'
            else:
                val = abs(led.total_value)
                data['debit'] = val
                if account_group not in ["Sundry Debtors", "Sundry Creditors"]:
                    total['debit_total'] += val
                data['credit'] = '-'

        # Use the ledger name as a key to avoid redundancy
        ledger_name = data['ledger']
        if ledger_name not in ledger_dict:
            ledger_dict[ledger_name] = data

    # Convert the dictionary values to a list
    ledger_entries = list(ledger_dict.values())

    for entry in ledger_entries:
        real_account_type = entry['account_type']
        account_type = entry['group']
        account_group = entry['group']


        # Check if the account_type already exists in trial_balance
        account_type_entry = next((d for d in trial_balance if d['account_type'] == account_type), None)

        if not account_type_entry:
            trial_balance.append({'real_account_type': real_account_type, 'account_type': account_type, 'groups': [{'group': account_group, 'ledgers': [entry]}]})
        else:
            # Find the dictionary for the current account_type
            current_account_type = next((d for d in trial_balance if d['account_type'] == account_type), None)

            # Check if the account_group already exists for the current account_type
            account_group_entry = next((g for g in current_account_type['groups'] if g['group'] == account_group), None)

            if not account_group_entry:
                current_account_type['groups'].append({'group': account_group, 'ledgers': [entry]})
            else:
                account_group_entry['ledgers'].append(entry)

    trial_balance = [dict(item) for item in trial_balance]
    vat_receivable = AccountLedger.objects.get(ledger_name= 'VAT Receivable')
    vat_payable = AccountLedger.objects.get(ledger_name= 'VAT Payable')



    vat_receivable_val = vat_receivable.total_value
    vat_payable_val = vat_payable.total_value

    print(f"vat_receivable {vat_receivable_val}")
    print(f"vat_payable {vat_payable_val}")

    vat = vat_receivable_val - vat_payable_val
    if vat > 0:
        vatreceivable_subledgers = AccountSubLedger.objects.filter(ledger__ledger_name= 'VAT Receivable')
        vatreceivable_subledger_entries = []
        for subledger in vatreceivable_subledgers:
            subledger_data = {
                    'subledger': subledger.sub_ledger_name,
                    'total_value': subledger.total_value
                }
            vatreceivable_subledger_entries.append(subledger_data)  
        new_vat_receivable_entry = {'real_account_type': vat_receivable.account_chart.account_type, 'account_type': vat_receivable.account_chart.group, 'groups': [{'group': vat_receivable.account_chart.group,"ledgers": [{'ledger': vat_receivable.ledger_name, 'group': vat_receivable.account_chart.account_type, 'debit': abs(vat), 'credit': 0, 'subledgers': vatreceivable_subledger_entries}] }]}
        total['debit_total'] += abs(vat)
        # total['credit_total'] += abs(vat)
        trial_balance.append(new_vat_receivable_entry)
    else:
        vatpayable_subledgers = AccountSubLedger.objects.filter(ledger__ledger_name= 'VAT Payable')
        vatpayable_subledger_entries = []
        for subledger in vatpayable_subledgers:
            subledger_data = {
                    'subledger': subledger.sub_ledger_name,
                    'total_value': subledger.total_value
                }
            vatpayable_subledger_entries.append(subledger_data)  
        new_vat_payable_entry = {'real_account_type': vat_payable.account_chart.account_type, 'account_type': vat_payable.account_chart.group, 'groups': [{'group': vat_payable.account_chart.group,"ledgers": [{'ledger': vat_payable.ledger_name, 'group': vat_payable.account_chart.account_type, 'debit': 0, 'credit': abs(vat), 'subledgers': vatpayable_subledger_entries}] }]}
        total['credit_total'] += abs(vat)
        trial_balance.append(new_vat_payable_entry)


    trial_balance.sort(key=lambda x: x['real_account_type'])

    Sundry_debtors_debit_total = 0
    Sundry_debtors_credit_total = 0
    Sundry_creditors_debit_total = 0
    Sundry_creditors_credit_total = 0
    new_ledgers_asset = []
    new_ledgers_liability = []


    for entry in trial_balance:
        new_ledger_entries = []
        for datas in entry['groups']:
            for data in datas['ledgers']:
                group = data.get('group')
                if group == 'Sundry Debtors':
                    if(data.get('debit') != '-'):
                        Sundry_debtors_debit_total += data.get('debit')

                    if(data.get('credit') != '-'):    
                        Sundry_debtors_credit_total += data.get('credit')

                elif group == 'Sundry Creditors':
                    if(data.get('credit') != '-'):
                            Sundry_creditors_credit_total += data.get('credit')
                    if(data.get('debit') != '-'):
                            Sundry_creditors_debit_total += data.get('debit')
                else:
                    new_ledger_entries.append(data)  # Keep all other ledgers
                
        datas['ledgers'] = new_ledger_entries  # Replace ledgers with the filtered list

        # Create new ledger entries for Sundry Debtors and add to the Asset section
    if (Sundry_debtors_debit_total != 0) or (Sundry_debtors_credit_total !=0):
        Sundry_debtors_debit_total_after = 0
        Sundry_debtors_credit_total_after = 0

        sundry_debtors_total = Sundry_debtors_debit_total - Sundry_debtors_credit_total
        if sundry_debtors_total > 0:
            Sundry_debtors_debit_total_after = sundry_debtors_total
            total['debit_total'] += Sundry_debtors_debit_total_after
            Sundry_debtors_credit_total_after = "-"
        else:
            Sundry_debtors_debit_total_after = "-"
            Sundry_debtors_credit_total_after = abs(sundry_debtors_total)
            total['credit_total'] += Sundry_debtors_credit_total_after
                
        ledgers = AccountLedger.objects.filter(account_chart__group="Sundry Debtors")
        subledger_entries = []

        for ledger in ledgers:
            subledger_data = {
                'subledger': ledger.ledger_name,
                'total_value': ledger.total_value
            }
            subledger_entries.append(subledger_data)
                
        new_sundry_debtors_entry = {'ledger': 'Sundry Debtors', 'group': 'Asset', 'debit': Sundry_debtors_debit_total_after, 'credit': Sundry_debtors_credit_total_after, 'subledgers': subledger_entries}
        new_ledgers_asset.append(new_sundry_debtors_entry)

        # Create new ledger entries for Sundry Creditors and add to the Liability section
    if (Sundry_creditors_debit_total != 0) or (Sundry_creditors_credit_total!= 0):
        Sundry_creditors_debit_total_after = 0
        Sundry_creditors_credit_total_after = 0

        sundry_creditors_total = Sundry_creditors_credit_total - Sundry_creditors_debit_total
        if sundry_creditors_total > 0:
            Sundry_creditors_debit_total_after = "-" 
            Sundry_creditors_credit_total_after = sundry_creditors_total
            total['credit_total'] += Sundry_creditors_credit_total_after
        else:
            Sundry_creditors_debit_total_after = abs(sundry_creditors_total)
            total['debit_total'] += Sundry_creditors_debit_total_after
            Sundry_creditors_credit_total_after = "-"

        ledgers = AccountLedger.objects.filter(account_chart__group="Sundry Creditors")
        subledger_entries = []

        for ledger in ledgers:
            subledger_data = {
                'subledger': ledger.ledger_name,
                'total_value': ledger.total_value
            }
            subledger_entries.append(subledger_data)
                
        new_sundry_creditors_entry = {'ledger': 'Sundry Creditors', 'group': 'Liability', 'debit': Sundry_creditors_debit_total_after, 'credit': Sundry_creditors_credit_total_after, 'subledgers': subledger_entries}
        new_ledgers_liability.append(new_sundry_creditors_entry)


        # Add the new ledger entries to the respective sections
    for entry in trial_balance:
        for groups in entry['groups']:

            if entry['real_account_type'] == 'Asset' and groups['group'] == 'Sundry Debtors':
                groups['ledgers'] = new_ledgers_asset
                #     entry['group'] = "Sundry Debtors"
            elif entry['real_account_type'] == 'Liability' and groups['group'] == 'Sundry Creditors':
                groups['ledgers'] = new_ledgers_liability
                entry['group'] = "Sundry Creditors"

    # context = {
    #     'trial_balance': trial_balance,
    #     "total": total,
    #     # "from_date":from_date,
    #     # "to_date":to_date,
    #     # 'current_fiscal_year':current_fiscal_year,
    #     # 'first_date': first_date,
    #     # 'last_date': last_date,
    #     'trial_active' : Organization.objects.first().show_zero_ledgers

    # }

    return trial_balance, total


def give_detail_expanded_sundry(from_date, to_date, group=None):
    """
    Same as give_detail(), but Sundry Debtors / Sundry Creditors are NOT
    aggregated into one control-account row. Each underlying AccountLedger
    (e.g. individual customer/vendor) is treated like any other ledger —
    own debit/credit/opening/closing computed, grouped normally under
    account_group 'Sundry Debtors' / 'Sundry Creditors' — so multiple
    ledgers can appear side by side under that group instead of being
    hidden inside a single row's 'subledgers'.
    """
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)

    org = Organization.objects.last()
    show_zero_ledgers = org.show_zero_ledgers

    all_ledgers = AccountLedger.objects.select_related('account_chart').all()
    if group is not None:
        all_ledgers = all_ledgers.filter(account_chart=group)

    all_ledger_ids = [l.id for l in all_ledgers]

    before_transactions = CumulativeLedger.objects.filter(entry_date__lt=from_date, ledger_id__in=all_ledger_ids)
    filtered_transactions = CumulativeLedger.objects.filter(
        Q(entry_date__range=[from_date, to_date]),
        Q(debit_amount__gt=0) | Q(credit_amount__gt=0),
        ledger_id__in=all_ledger_ids
    )

    filtered_sum = filtered_transactions.values(
        'ledger_name', 'account_chart__account_type', 'account_chart__group', 'ledger'
    ).annotate(
        debit=Sum('debit_amount'),
        credit=Sum('credit_amount')
    )

    opening_balances = defaultdict(lambda: 0)
    before_sums = before_transactions.values('ledger_name', 'account_chart__account_type').annotate(
        total_debit=Sum('debit_amount'),
        total_credit=Sum('credit_amount')
    )
    for item in before_sums:
        key = item['ledger_name']
        acc_type = item['account_chart__account_type']
        if acc_type in ['Asset', 'Expense']:
            opening_balances[key] = (item['total_debit'] or 0) - (item['total_credit'] or 0)
        else:
            opening_balances[key] = (item['total_credit'] or 0) - (item['total_debit'] or 0)

    ledger_dict = {}
    total = {'debit_total': 0, 'credit_total': 0}

    for led in filtered_sum:
        name = led['ledger_name']
        acc_type = led['account_chart__account_type']
        grp = led['account_chart__group']
        id_ = led['ledger']
        debit = led['debit'] or 0
        credit = led['credit'] or 0
        opening = opening_balances.get(name, 0)

        subledger_filter = Q(ledger_id=id_)
        if not show_zero_ledgers:
            subledger_filter &= Q(total_value__gt=0.0)
        subledgers = AccountSubLedger.objects.filter(subledger_filter)
        subledger_entries = get_subledger_data(from_date, to_date, subledgers)

        data = {
            'account_type': acc_type,
            'ledger': name,
            'group': grp,
            'id': id_,
            'opening': opening,
            'subledgers': subledger_entries,
            'debit': debit,
            'credit': credit,
        }

        # No exclusion for Sundry Debtors/Creditors here — every ledger gets its
        # own closing balance and contributes its real debit/credit to totals.
        total['debit_total'] += debit
        total['credit_total'] += credit
        if acc_type in ['Asset', 'Expense']:
            data['closing'] = opening + debit - credit
        else:
            data['closing'] = opening + credit - debit

        ledger_dict[name] = data

    for ledger in all_ledgers:
        if ledger.ledger_name in ledger_dict:
            continue

        name = ledger.ledger_name
        acc_type = ledger.account_chart.account_type
        grp = ledger.account_chart.group
        id_ = ledger.id
        opening = opening_balances.get(name, 0)

        if CumulativeLedger.objects.filter(ledger_id=id_, total_value__gt=0).exists():
            subledger_filter = Q(ledger_id=id_)
            if not show_zero_ledgers:
                subledger_filter &= Q(total_value__gt=0.0)
            subledgers = AccountSubLedger.objects.filter(subledger_filter)
            subledger_entries = get_subledger_data(from_date, to_date, subledgers)

            ledger_dict[name] = {
                'account_type': acc_type,
                'ledger': name,
                'group': grp,
                'id': id_,
                'opening': opening,
                'subledgers': subledger_entries,
                'debit': 0,
                'credit': 0,
                'closing': opening,
            }

    trial_balance_map = defaultdict(lambda: defaultdict(list))
    for data in ledger_dict.values():
        trial_balance_map[data['account_type']][data['group']].append(data)

    trial_balance = []
    for acc_type, groups in trial_balance_map.items():
        group_list = [{'group': grp, 'ledgers': ledgers} for grp, ledgers in groups.items()]
        trial_balance.append({'real_account_type': acc_type, 'account_type': acc_type, 'groups': group_list})

    trial_balance.sort(key=lambda x: x['real_account_type'])

    return trial_balance, total