# from accounting.models import AccountChart, AccountLedger, TblCrJournalEntry, TblJournalEntry, TblDrJournalEntry, CumulativeLedger
# from accounting.models import AccountSubLedger, AccountLedger, AccountChart
# from purchase.models import AccountProductTracking
# from decimal import Decimal
# from product.models import Product

# """
# Signal to update Cumulative Ledger
# """
# from datetime import date
# def update_cumulative_ledger_accounting(instance, entry_date):
#     ledger = CumulativeLedger.objects.filter(ledger=instance).last()
#     if ledger :
#         total_value = ledger.total_value
#     else:
#         total_value = Decimal(0.0)
#     value_changed = instance.total_value - total_value
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         if value_changed > 0:
#                 CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
#     else:
#         if value_changed > 0:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)

# # def create_cumulative_ledger_accounting(instance, entry_date):
# #     if instance.account_chart.account_type in ['Asset', 'Expense']:
# #         CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, debit_amount=instance.total_value, entry_date=entry_date)
# #     else:
# #         CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, credit_amount=instance.total_value, entry_date=entry_date)



# def create_cumulative_ledger_accounting(instance, entry_date, is_opening=False):
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         CumulativeLedger.objects.create(
#             account_chart=instance.account_chart,
#             ledger_name=instance.ledger_name,
#             total_value=instance.total_value,
#             value_changed=instance.total_value,
#             ledger=instance,
#             debit_amount=instance.total_value,
#             entry_date=entry_date,
#             is_opening=is_opening,
#         )
#     else:
#         CumulativeLedger.objects.create(
#             account_chart=instance.account_chart,
#             ledger_name=instance.ledger_name,
#             total_value=instance.total_value,
#             value_changed=instance.total_value,
#             ledger=instance,
#             credit_amount=instance.total_value,
#             entry_date=entry_date,
#             is_opening=is_opening,
#         )


# from datetime import date
# def update_cumulative_ledger_bill(instance, entry_date, journal_entry):
#     ledger = CumulativeLedger.objects.filter(ledger=instance).last()
#     if ledger :
#         total_value = ledger.total_value
#     else:
#         total_value = Decimal(0.0)
#     value_changed = instance.total_value - total_value
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         if value_changed > 0:
#                 CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
#     else:
#         if value_changed > 0:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)

# def update_cumulative_ledger_expense(instance, journal, entry_datetime):
#     ledger = CumulativeLedger.objects.filter(ledger=instance).last()
#     if ledger :
#         total_value = ledger.total_value
#     else:
#         total_value = Decimal(0.0)
#     value_changed = instance.total_value - total_value
#     print(value_changed)
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         if value_changed > 0:
#                 CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
#     else:
#         if value_changed > 0:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)

# def create_cumulative_ledger_bill(instance, entry_date, journal_entry):
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, debit_amount=instance.total_value, entry_date=entry_date, journal=journal_entry)
#     else:
#         CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, credit_amount=instance.total_value, entry_date=entry_date, journal=journal_entry)



# def create_journal_for_complimentary(instance):
#     grand_total = Decimal(instance.sub_total)
#     complimentary_sales = AccountLedger.objects.get(ledger_name__iexact='complimentary sales')
#     complimentary_expenses = AccountLedger.objects.get(ledger_name__iexact='complimentary expenses')
#     entry_date = instance.transaction_date_time

#     journal_entry = TblJournalEntry.objects.create(employee_name='Created automatically during sale', journal_total=grand_total, bill_id=instance.id)
#     TblDrJournalEntry.objects.create(particulars="Complimentary Expenses A/C Dr.", debit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_expenses)
#     TblCrJournalEntry.objects.create(particulars="To Complimentary Sales", credit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_sales)
    
#     complimentary_expenses.total_value += grand_total
#     complimentary_expenses.save()
#     update_cumulative_ledger_bill(complimentary_expenses, entry_date, journal_entry)

#     complimentary_sales.total_value += grand_total
#     complimentary_sales.save()
#     update_cumulative_ledger_bill(complimentary_sales, entry_date, journal_entry)


# def create_journal_for_bill(instance):
#     print(instance.amount_in_words)
#     payment_mode = instance.payment_mode.lower().strip()
#     print(payment_mode)
    
#     grand_total = Decimal(instance.grand_total)
#     tax_amount = Decimal(instance.tax_amount)
#     discount_amount = Decimal(instance.discount_amount)
#     invoice_number = instance.invoice_number
#     entry_date = instance.transaction_date_time
#     sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
#     journal_entry = TblJournalEntry.objects.create(employee_name=f'{instance.agent_name}', journal_total=(grand_total-discount_amount), entry_date=entry_date, bill_id=instance.id, narration=f'Created Automatically during Sale from bill no {invoice_number}')


#     if discount_amount > 0:
#         discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
#         discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

#         TblDrJournalEntry.objects.create(particulars="Discount Expenses A/C Dr.", debit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_expenses)
#         TblCrJournalEntry.objects.create(particulars="To Discount Sales", credit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_sales)
        
#         discount_expenses.total_value += discount_amount
#         discount_expenses.save()
#         # update_cumulative_ledger_bill(discount_expenses, entry_date)
#         update_cumulative_ledger_bill(discount_expenses, entry_date, journal_entry)

#         discount_sales.total_value += discount_amount
#         discount_sales.save()
#         # update_cumulative_ledger_bill(discount_sales, entry_date)
#         update_cumulative_ledger_bill(discount_sales, entry_date, journal_entry)


#     if tax_amount > 0:
#         vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
#         vat_payable.total_value = vat_payable.total_value + tax_amount
#         vat_payable.save()
#         # update_cumulative_ledger_bill(vat_payable, entry_date)
#         update_cumulative_ledger_bill(vat_payable, entry_date, journal_entry)

#         TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To VAT Payable", ledger=vat_payable, credit_amount=tax_amount)

#     if payment_mode == 'credit':
#         account_chart = AccountChart.objects.get(group='Sundry Debtors')
#         try:
#             dr_ledger = AccountLedger.objects.get(ledger_name=f'{instance.customer.pk} - {instance.customer.name}')
#             dr_ledger.total_value += grand_total
#             dr_ledger.save()
#             # update_cumulative_ledger_bill(dr_ledger, entry_date)
#             update_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

#         except AccountLedger.DoesNotExist:
#             dr_ledger = AccountLedger.objects.create(ledger_name=f'{instance.customer.pk} - {instance.customer.name}', account_chart=account_chart, total_value=grand_total)
#             entry_date = instance.transaction_date_time
#             # create_cumulative_ledger_bill(dr_ledger, entry_date)
#             create_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

#         TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr", ledger=dr_ledger, debit_amount=grand_total)
#         TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        
        
#     elif payment_mode == "credit card":
#         card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
#         TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Card Transaction A/C Dr", ledger=card_transaction_ledger, debit_amount=grand_total)
#         TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
#         card_transaction_ledger.total_value += grand_total
#         card_transaction_ledger.save()
#         # update_cumulative_ledger_bill(card_transaction_ledger, entry_date)
#         update_cumulative_ledger_bill(card_transaction_ledger, entry_date, journal_entry)

#     elif payment_mode == "mobile payment":
#         mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')

#         TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Mobile Payment A/C Dr", ledger=mobile_payment, debit_amount=grand_total)
#         TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
#         mobile_payment.total_value += grand_total
#         mobile_payment.save()
#         # update_cumulative_ledger_bill(mobile_payment, entry_date)
#         update_cumulative_ledger_bill(mobile_payment, entry_date, journal_entry)

#     elif payment_mode == "cash":
#         cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
#         cash_ledger.total_value = cash_ledger.total_value + grand_total
#         cash_ledger.save()
#         # update_cumulative_ledger_bill(cash_ledger, entry_date)
#         update_cumulative_ledger_bill(cash_ledger, entry_date, journal_entry)

#         TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Sales from invoice number {invoice_number} Cash A/C Dr", ledger=cash_ledger, debit_amount=grand_total)
#         TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))

#     sale_ledger.total_value += (grand_total-tax_amount)
#     sale_ledger.save()
#     # update_cumulative_ledger_bill(sale_ledger, entry_date)
#     update_cumulative_ledger_bill(sale_ledger, entry_date, journal_entry)

# def update_subledger_after_updating_product(product_id, initial_name, updated_name):
#     product = Product.objects.get(pk=product_id)
#     subledgername = f'{initial_name} ({product.category.title})'
#     AccountSubLedger.objects.filter(sub_ledger_name=subledgername).update(sub_ledger_name=f"{updated_name} ({product.category.title})")
    
# from accounting.models import AccountSubLedgerTracking
# def product_sold(instance):

#     print("sold instance", instance)


#     product = instance.product

#     print("sold product", product)
#     subledgername = f'{product.title} {product.id} - Sale'
    
#     sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
#     try:
#         print("I was in try")        
#         sale_subledger = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=sale_ledger)
#         prev_value = sale_subledger.total_value
#         subledgertracking = AccountSubLedgerTracking.objects.create(subledger = sale_subledger, prev_amount= sale_subledger.total_value)
#         sale_subledger.total_value += Decimal(instance.amount)
#         sale_subledger.save()
#         subledgertracking.new_amount=sale_subledger.total_value
#         subledgertracking.value_changed = sale_subledger.total_value - prev_value
#         subledgertracking.save()


#     except AccountSubLedger.DoesNotExist:
#         print("I was in the exception")
#         subledger = AccountSubLedger.objects.create(sub_ledger_name=subledgername, ledger=sale_ledger, total_value=Decimal(instance.amount))
#         subledgertracking = AccountSubLedgerTracking.objects.create(subledger=subledger, new_amount=Decimal(instance.amount), value_changed=Decimal(instance.amount))

# from datetime import date
# def update_cumulative_ledger_partyledger(instance, entry_date, journal_entry):
#     ledger = CumulativeLedger.objects.filter(ledger=instance).last()
#     if ledger :
#         total_value = ledger.total_value
#     else:
#         total_value = Decimal(0.0)
#     value_changed = instance.total_value - total_value
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         if value_changed > 0:
#                 CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
#     else:
#         if value_changed > 0:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)


# def update_cumulative_ledger_accounting_opening(instance, entry_date, is_opening=False):
#     ledger = CumulativeLedger.objects.filter(ledger=instance).last()
#     total_value = ledger.total_value if ledger else Decimal(0.0)
#     value_changed = instance.total_value - total_value
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         if value_changed > 0:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)
#     else:
#         if value_changed > 0:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)
#         else:
#             CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)

    
# from rent.models import BillRent


# def get_opening_units(slot):
#     """Same logic as BillRent._get_old_units() — last non-voided bill's closing, or slot's initial reading."""
#     last_bill = (
#         BillRent.objects
#         .filter(slot=slot, is_deleted=False)
#         .order_by('-bill_month')
#         .first()
#     )
#     if last_bill:
#         return last_bill.nea_current_unit, last_bill.diesel_current_unit
#     return slot.initial_nea_reading, slot.initial_diesel_reading



    

# from datetime import datetime
# from decimal import Decimal

# def finalize_rental_bill_accounting(bill):
#     """
#     Call this AFTER bill.recalculate_rental_totals() has set real
#     sub_total/taxable_amount/tax_amount/grand_total on a RENTAL bill.
#     Mirrors what create_invoice_number's signal does for non-rental bills,
#     but using final totals instead of the zeros present at creation time.
#     """
#     from bill.models import TblSalesEntry, TblTaxEntry


#     a = TblTaxEntry(
#         fiscal_year=bill.fiscal_year,
#         bill_no=bill.invoice_number,
#         customer_name=bill.customer_name,
#         customer_pan=bill.customer_tax_number,
#         bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
#         amount=bill.grand_total,
#         taxable_amount=bill.taxable_amount,
#         tax_amount=bill.tax_amount,
#         is_printed="Yes",
#         printed_time=str(datetime.now().time().strftime("%I:%M %p")),
#         entered_by=bill.agent_name,
#         printed_by=bill.agent_name,
#         is_realtime="Yes",
#         sync_with_ird="Yes",
#         payment_method=bill.payment_mode,
#         vat_refund_amount=0.0,
#         transaction_id="-",
#     )

#     b = TblSalesEntry(
#         bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
#         customer_name=bill.customer_name,
#         customer_pan=bill.customer_tax_number,
#         amount=bill.grand_total,
#         NoTaxSales=bill.grand_total - bill.tax_amount -bill.taxable_amount,
#         ZeroTaxSales=0.0,
#         taxable_amount=bill.taxable_amount,
#         tax_amount=bill.tax_amount,
#         miti=str(bill.transaction_miti),
#         ServicedItem="Goods",
#         quantity=1.0,
#         bill_no=bill.invoice_number,
#         excise_duty_amount=bill.excise_duty_amount,
#     )

#     if bill.tax_amount == 0:
#         a.exemptedSales = bill.sub_total
#         b.exemptedSales = bill.sub_total

#     if bill.payment_mode.lower().strip() == "complimentary":
#         try:
#             create_journal_for_complimentary(bill)
#         except Exception:
#             pass
#     else:
#         try:
#             create_journal_for_rental_bill(bill)   # was create_journal_for_bill
#         except Exception:
#             pass

#     b.save()
#     a.save()


# # bill/utils.py (or wherever create_journal_for_bill lives) -- add alongside it

# from decimal import Decimal
# from accounting.models import AccountSubLedger, AccountSubLedgerTracking


# def create_journal_for_other_bill(instance):
#     """
#     Same structure as create_journal_for_bill, EXCEPT the Sales credit line
#     is routed through an 'Others' subledger under the Sales ledger, so
#     Others-bill revenue (advertisement, misc income, etc.) is distinguishable
#     from regular product sales in reports, while the Sales ledger's
#     total_value stays consistent with the rest of the books.
#     """
#     payment_mode = instance.payment_mode.lower().strip()

#     grand_total = Decimal(instance.grand_total)
#     tax_amount = Decimal(instance.tax_amount)
#     discount_amount = Decimal(instance.discount_amount)
#     invoice_number = instance.invoice_number
#     entry_date = instance.transaction_date_time

#     sale_ledger = AccountLedger.objects.get(ledger_name='Sales')

#     # Get-or-create the 'Others' subledger under Sales.
#     others_subledger, _ = AccountSubLedger.objects.get_or_create(
#         sub_ledger_name='General',
#         ledger=sale_ledger,
#         defaults={'is_editable': True},
#     )

#     journal_entry = TblJournalEntry.objects.create(
#         employee_name=f'{instance.agent_name}',
#         journal_total=(grand_total - discount_amount),
#         entry_date=entry_date,
#         bill_id=instance.id,
#         narration=f'Created Automatically during Manual bill from bill no {invoice_number}',
#     )

#     if discount_amount > 0:
#         discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
#         discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

#         TblDrJournalEntry.objects.create(
#             particulars="Discount Expenses A/C Dr.", debit_amount=discount_amount,
#             journal_entry=journal_entry, ledger=discount_expenses
#         )
#         TblCrJournalEntry.objects.create(
#             particulars="To Discount Sales", credit_amount=discount_amount,
#             journal_entry=journal_entry, ledger=discount_sales
#         )

#         discount_expenses.total_value += discount_amount
#         discount_expenses.save()
#         update_cumulative_ledger_bill(discount_expenses, entry_date, journal_entry)

#         discount_sales.total_value += discount_amount
#         discount_sales.save()
#         update_cumulative_ledger_bill(discount_sales, entry_date, journal_entry)

#     if tax_amount > 0:
#         vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
#         vat_payable.total_value += tax_amount
#         vat_payable.save()
#         update_cumulative_ledger_bill(vat_payable, entry_date, journal_entry)

#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To VAT Payable",
#             ledger=vat_payable, credit_amount=tax_amount
#         )

#     if payment_mode == 'credit':
#         account_chart = AccountChart.objects.get(group='Sundry Debtors')
#         try:
#             dr_ledger = AccountLedger.objects.get(
#                 ledger_name=f'{instance.customer.pk} - {instance.customer.name}'
#             )
#             dr_ledger.total_value += grand_total
#             dr_ledger.save()
#             update_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)
#         except AccountLedger.DoesNotExist:
#             dr_ledger = AccountLedger.objects.create(
#                 ledger_name=f'{instance.customer.pk} - {instance.customer.name}',
#                 account_chart=account_chart, total_value=grand_total
#             )
#             create_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr",
#             ledger=dr_ledger, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Others",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=others_subledger,
#         )

#     elif payment_mode == "credit card":
#         card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="Card Transaction A/C Dr",
#             ledger=card_transaction_ledger, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Others",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=others_subledger,
#         )
#         card_transaction_ledger.total_value += grand_total
#         card_transaction_ledger.save()
#         update_cumulative_ledger_bill(card_transaction_ledger, entry_date, journal_entry)

#     elif payment_mode == "mobile payment":
#         mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')
#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="Mobile Payment A/C Dr",
#             ledger=mobile_payment, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Others",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=others_subledger,
#         )
#         mobile_payment.total_value += grand_total
#         mobile_payment.save()
#         update_cumulative_ledger_bill(mobile_payment, entry_date, journal_entry)

#     elif payment_mode == "cash":
#         cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
#         cash_ledger.total_value += grand_total
#         cash_ledger.save()
#         update_cumulative_ledger_bill(cash_ledger, entry_date, journal_entry)

#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry,
#             particulars=f"Others bill invoice {invoice_number} Cash A/C Dr",
#             ledger=cash_ledger, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Others",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=others_subledger,
#         )

#     # ---- Update Sales ledger total (same as create_journal_for_bill) ----
#     sale_ledger.total_value += (grand_total - tax_amount)
#     sale_ledger.save()
#     update_cumulative_ledger_bill(sale_ledger, entry_date, journal_entry)

#     # ---- Track the subledger movement (mirrors purchase's create_subledgers /
#     # JournalEntryCreateView's subledger tracking pattern) ----
#     prev_value = others_subledger.total_value
#     subledger_tracking = AccountSubLedgerTracking.objects.create(
#         subledger=others_subledger, prev_amount=prev_value, journal=journal_entry
#     )
#     others_subledger.total_value += (grand_total - tax_amount)
#     others_subledger.save()
#     subledger_tracking.new_amount = others_subledger.total_value
#     subledger_tracking.value_changed = others_subledger.total_value - prev_value
#     subledger_tracking.save()

# # bill/utils.py -- add alongside finalize_rental_bill_accounting

# from datetime import datetime
# from decimal import Decimal


# def finalize_other_bill_accounting(bill):
#     """
#     Call this AFTER bill.recalculate_other_totals() has set real
#     sub_total/taxable_amount/tax_amount/grand_total on an OTHERS bill.
#     Mirrors finalize_rental_bill_accounting exactly, reusing the same
#     create_journal_for_bill / create_journal_for_complimentary functions --
#     those are generic over bill_type (they read bill.grand_total /
#     bill.tax_amount / bill.payment_mode, not per-item data), so no new
#     journal logic is needed here.
#     """
#     from bill.models import TblSalesEntry, TblTaxEntry

#     a = TblTaxEntry(
#         fiscal_year=bill.fiscal_year,
#         bill_no=bill.invoice_number,
#         customer_name=bill.customer_name,
#         customer_pan=bill.customer_tax_number,
#         bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
#         amount=bill.grand_total,
#         taxable_amount=bill.taxable_amount,
#         tax_amount=bill.tax_amount,
#         is_printed="Yes",
#         printed_time=str(datetime.now().time().strftime("%I:%M %p")),
#         entered_by=bill.agent_name,
#         printed_by=bill.agent_name,
#         is_realtime="Yes",
#         sync_with_ird="Yes",
#         payment_method=bill.payment_mode,
#         vat_refund_amount=0.0,
#         transaction_id="-",
#     )

#     b = TblSalesEntry(
#         bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
#         customer_name=bill.customer_name,
#         customer_pan=bill.customer_tax_number,
#         amount=bill.grand_total,
#         NoTaxSales=bill.grand_total - bill.tax_amount -bill.taxable_amount,
#         ZeroTaxSales=0.0,
#         taxable_amount=bill.taxable_amount,
#         tax_amount=bill.tax_amount,
#         miti=str(bill.transaction_miti),
#         ServicedItem="Others",  # only difference from the rental version ("Goods")
#         quantity=1.0,
#         bill_no=bill.invoice_number,
#         excise_duty_amount=bill.excise_duty_amount,
#     )

#     if bill.tax_amount == 0:
#         a.exemptedSales = bill.sub_total
#         b.exemptedSales = bill.sub_total

#     if bill.payment_mode.lower().strip() == "complimentary":
#         try:
#             create_journal_for_complimentary(bill)
#         except Exception:
#             pass
#     else:
#         try:
#             create_journal_for_other_bill(bill)
#         except Exception:
#             pass

#     b.save()
#     a.save()


# from decimal import Decimal
# from accounting.models import AccountSubLedger, AccountSubLedgerTracking


# def create_journal_for_rental_bill(instance):
#     """
#     Same structure as create_journal_for_other_bill, EXCEPT the Sales credit
#     line is routed through a 'Rental' subledger under the Sales ledger, so
#     rental revenue is distinguishable from regular product sales and Others
#     revenue in reports, while the Sales ledger's total_value stays
#     consistent with the rest of the books.
#     """
#     payment_mode = instance.payment_mode.lower().strip()

#     grand_total = Decimal(instance.grand_total)
#     tax_amount = Decimal(instance.tax_amount)
#     discount_amount = Decimal(instance.discount_amount)
#     invoice_number = instance.invoice_number
#     entry_date = instance.transaction_date_time

#     sale_ledger = AccountLedger.objects.get(ledger_name='Sales')

#     # Get-or-create the 'Rental' subledger under Sales.
#     rental_subledger, _ = AccountSubLedger.objects.get_or_create(
#         sub_ledger_name='Rental',
#         ledger=sale_ledger,
#         defaults={'is_editable': True},
#     )

#     journal_entry = TblJournalEntry.objects.create(
#         employee_name=f'{instance.agent_name}',
#         journal_total=(grand_total - discount_amount),
#         entry_date=entry_date,
#         bill_id=instance.id,
#         narration=f'Created Automatically during Rental bill from bill no {invoice_number}',
#     )

#     if discount_amount > 0:
#         discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
#         discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

#         TblDrJournalEntry.objects.create(
#             particulars="Discount Expenses A/C Dr.", debit_amount=discount_amount,
#             journal_entry=journal_entry, ledger=discount_expenses
#         )
#         TblCrJournalEntry.objects.create(
#             particulars="To Discount Sales", credit_amount=discount_amount,
#             journal_entry=journal_entry, ledger=discount_sales
#         )

#         discount_expenses.total_value += discount_amount
#         discount_expenses.save()
#         update_cumulative_ledger_bill(discount_expenses, entry_date, journal_entry)

#         discount_sales.total_value += discount_amount
#         discount_sales.save()
#         update_cumulative_ledger_bill(discount_sales, entry_date, journal_entry)

#     if tax_amount > 0:
#         vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
#         vat_payable.total_value += tax_amount
#         vat_payable.save()
#         update_cumulative_ledger_bill(vat_payable, entry_date, journal_entry)

#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To VAT Payable",
#             ledger=vat_payable, credit_amount=tax_amount
#         )

#     if payment_mode == 'credit':
#         account_chart = AccountChart.objects.get(group='Sundry Debtors')
#         try:
#             dr_ledger = AccountLedger.objects.get(
#                 ledger_name=f'{instance.customer.pk} - {instance.customer.name}'
#             )
#             dr_ledger.total_value += grand_total
#             dr_ledger.save()
#             update_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)
#         except AccountLedger.DoesNotExist:
#             dr_ledger = AccountLedger.objects.create(
#                 ledger_name=f'{instance.customer.pk} - {instance.customer.name}',
#                 account_chart=account_chart, total_value=grand_total
#             )
#             create_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr",
#             ledger=dr_ledger, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Rental",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=rental_subledger,
#         )

#     elif payment_mode == "credit card":
#         card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="Card Transaction A/C Dr",
#             ledger=card_transaction_ledger, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Rental",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=rental_subledger,
#         )
#         card_transaction_ledger.total_value += grand_total
#         card_transaction_ledger.save()
#         update_cumulative_ledger_bill(card_transaction_ledger, entry_date, journal_entry)

#     elif payment_mode == "mobile payment":
#         mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')
#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="Mobile Payment A/C Dr",
#             ledger=mobile_payment, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Rental",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=rental_subledger,
#         )
#         mobile_payment.total_value += grand_total
#         mobile_payment.save()
#         update_cumulative_ledger_bill(mobile_payment, entry_date, journal_entry)

#     elif payment_mode == "cash":
#         cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
#         cash_ledger.total_value += grand_total
#         cash_ledger.save()
#         update_cumulative_ledger_bill(cash_ledger, entry_date, journal_entry)

#         TblDrJournalEntry.objects.create(
#             journal_entry=journal_entry,
#             particulars=f"Rental bill invoice {invoice_number} Cash A/C Dr",
#             ledger=cash_ledger, debit_amount=grand_total
#         )
#         TblCrJournalEntry.objects.create(
#             journal_entry=journal_entry, particulars="To Sales - Rental",
#             ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
#             sub_ledger=rental_subledger,
#         )

#     # ---- Update Sales ledger total (same as create_journal_for_bill) ----
#     sale_ledger.total_value += (grand_total - tax_amount)
#     sale_ledger.save()
#     update_cumulative_ledger_bill(sale_ledger, entry_date, journal_entry)

#     # ---- Track the subledger movement ----
#     prev_value = rental_subledger.total_value
#     subledger_tracking = AccountSubLedgerTracking.objects.create(
#         subledger=rental_subledger, prev_amount=prev_value, journal=journal_entry
#     )
#     rental_subledger.total_value += (grand_total - tax_amount)
#     rental_subledger.save()
#     subledger_tracking.new_amount = rental_subledger.total_value
#     subledger_tracking.value_changed = rental_subledger.total_value - prev_value
#     subledger_tracking.save()


from accounting.models import AccountChart, AccountLedger, TblCrJournalEntry, TblJournalEntry, TblDrJournalEntry, CumulativeLedger
from accounting.models import AccountSubLedger, AccountLedger, AccountChart
from purchase.models import AccountProductTracking
from decimal import Decimal
from product.models import Product

"""
Signal to update Cumulative Ledger
"""
from datetime import date
def update_cumulative_ledger_accounting(instance, entry_date):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date)

# def create_cumulative_ledger_accounting(instance, entry_date):
#     if instance.account_chart.account_type in ['Asset', 'Expense']:
#         CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, debit_amount=instance.total_value, entry_date=entry_date)
#     else:
#         CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, credit_amount=instance.total_value, entry_date=entry_date)



def create_cumulative_ledger_accounting(instance, entry_date, is_opening=False):
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        CumulativeLedger.objects.create(
            account_chart=instance.account_chart,
            ledger_name=instance.ledger_name,
            total_value=instance.total_value,
            value_changed=instance.total_value,
            ledger=instance,
            debit_amount=instance.total_value,
            entry_date=entry_date,
            is_opening=is_opening,
        )
    else:
        CumulativeLedger.objects.create(
            account_chart=instance.account_chart,
            ledger_name=instance.ledger_name,
            total_value=instance.total_value,
            value_changed=instance.total_value,
            ledger=instance,
            credit_amount=instance.total_value,
            entry_date=entry_date,
            is_opening=is_opening,
        )


from datetime import date
def update_cumulative_ledger_bill(instance, entry_date, journal_entry):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal=journal_entry)

def update_cumulative_ledger_expense(instance, journal, entry_datetime):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    print(value_changed)
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, journal=journal, entry_date=entry_datetime)

def create_cumulative_ledger_bill(instance, entry_date, journal_entry):
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, debit_amount=instance.total_value, entry_date=entry_date, journal=journal_entry)
    else:
        CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=instance.total_value, ledger=instance, credit_amount=instance.total_value, entry_date=entry_date, journal=journal_entry)



def create_journal_for_complimentary(instance):
    grand_total = Decimal(instance.sub_total)
    complimentary_sales = AccountLedger.objects.get(ledger_name__iexact='complimentary sales')
    complimentary_expenses = AccountLedger.objects.get(ledger_name__iexact='complimentary expenses')
    entry_date = instance.transaction_date_time

    journal_entry = TblJournalEntry.objects.create(employee_name='Created automatically during sale', journal_total=grand_total, bill_id=instance.id)
    TblDrJournalEntry.objects.create(particulars="Complimentary Expenses A/C Dr.", debit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_expenses)
    TblCrJournalEntry.objects.create(particulars="To Complimentary Sales", credit_amount = grand_total, journal_entry=journal_entry, ledger=complimentary_sales)
    
    complimentary_expenses.total_value += grand_total
    complimentary_expenses.save()
    update_cumulative_ledger_bill(complimentary_expenses, entry_date, journal_entry)

    complimentary_sales.total_value += grand_total
    complimentary_sales.save()
    update_cumulative_ledger_bill(complimentary_sales, entry_date, journal_entry)


def create_journal_for_bill(instance):
    print(instance.amount_in_words)
    payment_mode = instance.payment_mode.lower().strip()
    print(payment_mode)
    
    grand_total = Decimal(instance.grand_total)
    tax_amount = Decimal(instance.tax_amount)
    discount_amount = Decimal(instance.discount_amount)
    invoice_number = instance.invoice_number
    entry_date = instance.transaction_date_time
    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    journal_entry = TblJournalEntry.objects.create(employee_name=f'{instance.agent_name}', journal_total=(grand_total-discount_amount), entry_date=entry_date, bill_id=instance.id, narration=f'Created Automatically during Sale from bill no {invoice_number}')


    if discount_amount > 0:
        discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
        discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

        TblDrJournalEntry.objects.create(particulars="Discount Expenses A/C Dr.", debit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_expenses)
        TblCrJournalEntry.objects.create(particulars="To Discount Sales", credit_amount = discount_amount, journal_entry=journal_entry, ledger=discount_sales)
        
        discount_expenses.total_value += discount_amount
        discount_expenses.save()
        # update_cumulative_ledger_bill(discount_expenses, entry_date)
        update_cumulative_ledger_bill(discount_expenses, entry_date, journal_entry)

        discount_sales.total_value += discount_amount
        discount_sales.save()
        # update_cumulative_ledger_bill(discount_sales, entry_date)
        update_cumulative_ledger_bill(discount_sales, entry_date, journal_entry)


    if tax_amount > 0:
        vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
        vat_payable.total_value = vat_payable.total_value + tax_amount
        vat_payable.save()
        # update_cumulative_ledger_bill(vat_payable, entry_date)
        update_cumulative_ledger_bill(vat_payable, entry_date, journal_entry)

        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To VAT Payable", ledger=vat_payable, credit_amount=tax_amount)

    if payment_mode == 'credit':
        account_chart = AccountChart.objects.get(group='Sundry Debtors')
        try:
            dr_ledger = AccountLedger.objects.get(ledger_name=f'{instance.customer.pk} - {instance.customer.name}')
            dr_ledger.total_value += grand_total
            dr_ledger.save()
            # update_cumulative_ledger_bill(dr_ledger, entry_date)
            update_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

        except AccountLedger.DoesNotExist:
            dr_ledger = AccountLedger.objects.create(ledger_name=f'{instance.customer.pk} - {instance.customer.name}', account_chart=account_chart, total_value=grand_total)
            entry_date = instance.transaction_date_time
            # create_cumulative_ledger_bill(dr_ledger, entry_date)
            create_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr", ledger=dr_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        
        
    elif payment_mode == "credit card":
        card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Card Transaction A/C Dr", ledger=card_transaction_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        card_transaction_ledger.total_value += grand_total
        card_transaction_ledger.save()
        # update_cumulative_ledger_bill(card_transaction_ledger, entry_date)
        update_cumulative_ledger_bill(card_transaction_ledger, entry_date, journal_entry)

    elif payment_mode == "mobile payment":
        mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Mobile Payment A/C Dr", ledger=mobile_payment, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))
        mobile_payment.total_value += grand_total
        mobile_payment.save()
        # update_cumulative_ledger_bill(mobile_payment, entry_date)
        update_cumulative_ledger_bill(mobile_payment, entry_date, journal_entry)

    elif payment_mode == "cash":
        cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
        cash_ledger.total_value = cash_ledger.total_value + grand_total
        cash_ledger.save()
        # update_cumulative_ledger_bill(cash_ledger, entry_date)
        update_cumulative_ledger_bill(cash_ledger, entry_date, journal_entry)

        TblDrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"Sales from invoice number {invoice_number} Cash A/C Dr", ledger=cash_ledger, debit_amount=grand_total)
        TblCrJournalEntry.objects.create(journal_entry=journal_entry, particulars=f"To Sales", ledger=sale_ledger, credit_amount=(grand_total-tax_amount))

    sale_ledger.total_value += (grand_total-tax_amount)
    sale_ledger.save()
    # update_cumulative_ledger_bill(sale_ledger, entry_date)
    update_cumulative_ledger_bill(sale_ledger, entry_date, journal_entry)

def update_subledger_after_updating_product(product_id, initial_name, updated_name):
    product = Product.objects.get(pk=product_id)
    subledgername = f'{initial_name} ({product.category.title})'
    AccountSubLedger.objects.filter(sub_ledger_name=subledgername).update(sub_ledger_name=f"{updated_name} ({product.category.title})")
    
from accounting.models import AccountSubLedgerTracking
def product_sold(instance):

    print("sold instance", instance)


    product = instance.product

    print("sold product", product)
    subledgername = f'{product.title} {product.id} - Sale'
    
    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')
    try:
        print("I was in try")        
        sale_subledger = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=sale_ledger)
        prev_value = sale_subledger.total_value
        subledgertracking = AccountSubLedgerTracking.objects.create(subledger = sale_subledger, prev_amount= sale_subledger.total_value)
        sale_subledger.total_value += Decimal(instance.amount)
        sale_subledger.save()
        subledgertracking.new_amount=sale_subledger.total_value
        subledgertracking.value_changed = sale_subledger.total_value - prev_value
        subledgertracking.save()


    except AccountSubLedger.DoesNotExist:
        print("I was in the exception")
        subledger = AccountSubLedger.objects.create(sub_ledger_name=subledgername, ledger=sale_ledger, total_value=Decimal(instance.amount))
        subledgertracking = AccountSubLedgerTracking.objects.create(subledger=subledger, new_amount=Decimal(instance.amount), value_changed=Decimal(instance.amount))

from datetime import date
def update_cumulative_ledger_partyledger(instance, entry_date, journal_entry):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    if ledger :
        total_value = ledger.total_value
    else:
        total_value = Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
                CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, journal = journal_entry)


def update_cumulative_ledger_accounting_opening(instance, entry_date, is_opening=False):
    ledger = CumulativeLedger.objects.filter(ledger=instance).last()
    total_value = ledger.total_value if ledger else Decimal(0.0)
    value_changed = instance.total_value - total_value
    if instance.account_chart.account_type in ['Asset', 'Expense']:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)
    else:
        if value_changed > 0:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, credit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)
        else:
            CumulativeLedger.objects.create(account_chart=instance.account_chart, ledger_name=instance.ledger_name, total_value=instance.total_value, value_changed=value_changed, debit_amount=abs(value_changed), ledger=instance, entry_date=entry_date, is_opening=is_opening)

    
from rent.models import BillRent


def get_opening_units(slot):
    """Same logic as BillRent._get_old_units() — last non-voided bill's closing, or slot's initial reading."""
    last_bill = (
        BillRent.objects
        .filter(slot=slot, is_deleted=False)
        .order_by('-bill_month')
        .first()
    )
    if last_bill:
        return last_bill.nea_current_unit, last_bill.diesel_current_unit
    return slot.initial_nea_reading, slot.initial_diesel_reading


from datetime import datetime
from decimal import Decimal
from django.utils import timezone


def finalize_rental_bill_accounting(bill):
    """
    Call this AFTER bill.recalculate_rental_totals() has set real
    sub_total/taxable_amount/tax_amount/grand_total on a RENTAL bill.

    Writes TblTaxEntry/TblSalesEntry UNCONDITIONALLY -- the bill and its
    ledger rows are saved regardless of whether IRD sync succeeds.
    sync_with_ird starts as "No" and is flipped to "Yes" later by
    attempt_ird_sync(), only on confirmed success.
    """
    from bill.models import TblSalesEntry, TblTaxEntry

    a = TblTaxEntry(
        fiscal_year=bill.fiscal_year,
        bill_no=bill.invoice_number,
        customer_name=bill.customer_name,
        customer_pan=bill.customer_tax_number,
        bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
        amount=bill.grand_total,
        taxable_amount=bill.taxable_amount,
        tax_amount=bill.tax_amount,
        is_printed="Yes",
        printed_time=str(datetime.now().time().strftime("%I:%M %p")),
        entered_by=bill.agent_name,
        printed_by=bill.agent_name,
        is_realtime="No",
        sync_with_ird="No",  # flipped to "Yes" only after a confirmed IRD success
        payment_method=bill.payment_mode,
        vat_refund_amount=0.0,
        transaction_id="-",
    )

    b = TblSalesEntry(
        bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
        customer_name=bill.customer_name,
        customer_pan=bill.customer_tax_number,
        amount=bill.grand_total,
        NoTaxSales=bill.grand_total - bill.tax_amount - bill.taxable_amount,
        ZeroTaxSales=0.0,
        taxable_amount=bill.taxable_amount,
        tax_amount=bill.tax_amount,
        miti=str(bill.transaction_miti),
        ServicedItem="Goods",
        quantity=1.0,
        bill_no=bill.invoice_number,
        excise_duty_amount=bill.excise_duty_amount,
        fiscal_year=bill.fiscal_year,
        ird_synced=True,
    )

    if bill.tax_amount == 0:
        a.exemptedSales = bill.sub_total
        b.exemptedSales = bill.sub_total

    if bill.payment_mode.lower().strip() == "complimentary":
        try:
            create_journal_for_complimentary(bill)
        except Exception:
            pass
    else:
        try:
            create_journal_for_rental_bill(bill)
        except Exception:
            pass

    b.save()
    a.save()

from django.db import transaction as db_transaction

IRD_CODE_MEANINGS = {
    100: "API credentials do not match",
    101: "Bill already exists",
    102: "Exception while saving bill details",
    103: "Unknown exception",
    104: "Model invalid",
    200: "Success",
}

def attempt_ird_sync(bill):
    from bill.models import TblTaxEntry
    from bill.ird.postbillintoird import build_bill_ird_payload, postbillintoird

    bill.ird_last_attempt_at = timezone.now()
    is_first_attempt = bill.ird_retry_count == 0  # capture BEFORE we might increment it

    try:
        payload = build_bill_ird_payload(bill)
        raw_response = postbillintoird(payload)

        response_body = raw_response[0] if isinstance(raw_response, tuple) else raw_response

        if isinstance(response_body, dict):
            ird_code = response_body.get('code') or response_body.get('Code')
        else:
            ird_code = response_body

        try:
            ird_code = int(ird_code)
        except (TypeError, ValueError):
            ird_code = None

        if ird_code in (200, 101):
            with db_transaction.atomic():
                bill.ird_synced = True
                bill.ird_sync_error = None if ird_code == 200 else "IRD reported bill already exists (code 101) -- treated as synced"
                bill.ird_response = str(response_body)
                bill.save(update_fields=['ird_synced', 'ird_sync_error', 'ird_last_attempt_at', 'ird_retry_count', 'ird_response'])
                TblTaxEntry.objects.filter(
                    bill_no=bill.invoice_number, fiscal_year=bill.fiscal_year
                ).update(
                    sync_with_ird="Yes",
                    is_realtime="Yes" if is_first_attempt else "No",
                )
            return bill.ird_synced

        meaning = IRD_CODE_MEANINGS.get(ird_code, "Unrecognized response")
        raise Exception(f"IRD code {ird_code} ({meaning}): {response_body}")

    except Exception as e:
        bill.ird_synced = False
        bill.ird_sync_error = str(e)
        bill.ird_retry_count = bill.ird_retry_count + 1
        try:
            bill.save(update_fields=['ird_synced', 'ird_sync_error', 'ird_last_attempt_at', 'ird_retry_count'])
        except Exception as save_error:
            import logging
            logging.getLogger(__name__).error(
                f"Failed to persist IRD sync failure for bill {bill.id}: {save_error} (original error: {e})"
            )
        return bill.ird_synced

def retry_previously_failed_ird_bills(exclude_ids=None, limit=25):
    exclude_ids = exclude_ids or []
    with db_transaction.atomic():
        from bill.models import Bill
        qs = list(
            Bill.objects
            .select_for_update()  # skip_locked removed -- not supported on MariaDB < 10.6
            .filter(ird_synced=False)
            .exclude(id__in=exclude_ids)
            .exclude(invoice_number__isnull=True)
            .order_by('ird_last_attempt_at')[:limit]
        )
    for bill in qs:
        try:
            attempt_ird_sync(bill)
        except Exception:
            continue

import logging
import threading
from django.db import connections

logger = logging.getLogger(__name__)


def _run_ird_retry_sweep_in_background(exclude_ids):
    """
    Runs on its own thread with its own DB connection(s). Must close them
    explicitly -- Django only auto-closes per-request connections on the
    main request thread, not on threads you spawn yourself.
    """
    logger.info("IRD retry sweep started, excluding %d bill(s)", len(exclude_ids))
    try:
        retry_previously_failed_ird_bills(exclude_ids=exclude_ids)
        logger.info("IRD retry sweep completed")
    except Exception:
        logger.exception("IRD retry sweep failed")
    finally:
        connections.close_all()


def start_ird_retry_sweep(exclude_ids):
    thread = threading.Thread(
        target=_run_ird_retry_sweep_in_background,
        args=(exclude_ids,),
        daemon=True,
    )
    thread.start()
# bill/utils.py (or wherever create_journal_for_bill lives) -- add alongside it

from decimal import Decimal
from accounting.models import AccountSubLedger, AccountSubLedgerTracking


def create_journal_for_other_bill(instance):
    """
    Same structure as create_journal_for_bill, EXCEPT the Sales credit line
    is routed through an 'Others' subledger under the Sales ledger, so
    Others-bill revenue (advertisement, misc income, etc.) is distinguishable
    from regular product sales in reports, while the Sales ledger's
    total_value stays consistent with the rest of the books.
    """
    payment_mode = instance.payment_mode.lower().strip()

    grand_total = Decimal(instance.grand_total)
    tax_amount = Decimal(instance.tax_amount)
    discount_amount = Decimal(instance.discount_amount)
    invoice_number = instance.invoice_number
    entry_date = instance.transaction_date_time

    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')

    # Get-or-create the 'Others' subledger under Sales.
    others_subledger, _ = AccountSubLedger.objects.get_or_create(
        sub_ledger_name='General',
        ledger=sale_ledger,
        defaults={'is_editable': True},
    )

    journal_entry = TblJournalEntry.objects.create(
        employee_name=f'{instance.agent_name}',
        journal_total=(grand_total - discount_amount),
        entry_date=entry_date,
        bill_id=instance.id,
        narration=f'Created Automatically during Manual bill from bill no {invoice_number}',
    )

    if discount_amount > 0:
        discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
        discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

        TblDrJournalEntry.objects.create(
            particulars="Discount Expenses A/C Dr.", debit_amount=discount_amount,
            journal_entry=journal_entry, ledger=discount_expenses
        )
        TblCrJournalEntry.objects.create(
            particulars="To Discount Sales", credit_amount=discount_amount,
            journal_entry=journal_entry, ledger=discount_sales
        )

        discount_expenses.total_value += discount_amount
        discount_expenses.save()
        update_cumulative_ledger_bill(discount_expenses, entry_date, journal_entry)

        discount_sales.total_value += discount_amount
        discount_sales.save()
        update_cumulative_ledger_bill(discount_sales, entry_date, journal_entry)

    if tax_amount > 0:
        vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
        vat_payable.total_value += tax_amount
        vat_payable.save()
        update_cumulative_ledger_bill(vat_payable, entry_date, journal_entry)

        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To VAT Payable",
            ledger=vat_payable, credit_amount=tax_amount
        )

    if payment_mode == 'credit':
        account_chart = AccountChart.objects.get(group='Sundry Debtors')
        try:
            dr_ledger = AccountLedger.objects.get(
                ledger_name=f'{instance.customer.pk} - {instance.customer.name}'
            )
            dr_ledger.total_value += grand_total
            dr_ledger.save()
            update_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)
        except AccountLedger.DoesNotExist:
            dr_ledger = AccountLedger.objects.create(
                ledger_name=f'{instance.customer.pk} - {instance.customer.name}',
                account_chart=account_chart, total_value=grand_total
            )
            create_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr",
            ledger=dr_ledger, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Others",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=others_subledger,
        )

    elif payment_mode == "credit card":
        card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="Card Transaction A/C Dr",
            ledger=card_transaction_ledger, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Others",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=others_subledger,
        )
        card_transaction_ledger.total_value += grand_total
        card_transaction_ledger.save()
        update_cumulative_ledger_bill(card_transaction_ledger, entry_date, journal_entry)

    elif payment_mode == "mobile payment":
        mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')
        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="Mobile Payment A/C Dr",
            ledger=mobile_payment, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Others",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=others_subledger,
        )
        mobile_payment.total_value += grand_total
        mobile_payment.save()
        update_cumulative_ledger_bill(mobile_payment, entry_date, journal_entry)

    elif payment_mode == "cash":
        cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
        cash_ledger.total_value += grand_total
        cash_ledger.save()
        update_cumulative_ledger_bill(cash_ledger, entry_date, journal_entry)

        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry,
            particulars=f"Others bill invoice {invoice_number} Cash A/C Dr",
            ledger=cash_ledger, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Others",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=others_subledger,
        )

    # ---- Update Sales ledger total (same as create_journal_for_bill) ----
    sale_ledger.total_value += (grand_total - tax_amount)
    sale_ledger.save()
    update_cumulative_ledger_bill(sale_ledger, entry_date, journal_entry)

    # ---- Track the subledger movement (mirrors purchase's create_subledgers /
    # JournalEntryCreateView's subledger tracking pattern) ----
    prev_value = others_subledger.total_value
    subledger_tracking = AccountSubLedgerTracking.objects.create(
        subledger=others_subledger, prev_amount=prev_value, journal=journal_entry
    )
    others_subledger.total_value += (grand_total - tax_amount)
    others_subledger.save()
    subledger_tracking.new_amount = others_subledger.total_value
    subledger_tracking.value_changed = others_subledger.total_value - prev_value
    subledger_tracking.save()

# bill/utils.py -- add alongside finalize_rental_bill_accounting

from datetime import datetime
from decimal import Decimal


def finalize_other_bill_accounting(bill):
    """
    Call this AFTER bill.recalculate_other_totals() has set real
    sub_total/taxable_amount/tax_amount/grand_total on an OTHERS bill.
    Mirrors finalize_rental_bill_accounting exactly, reusing the same
    create_journal_for_bill / create_journal_for_complimentary functions --
    those are generic over bill_type (they read bill.grand_total /
    bill.tax_amount / bill.payment_mode, not per-item data), so no new
    journal logic is needed here.
    """
    from bill.models import TblSalesEntry, TblTaxEntry

    a = TblTaxEntry(
        fiscal_year=bill.fiscal_year,
        bill_no=bill.invoice_number,
        customer_name=bill.customer_name,
        customer_pan=bill.customer_tax_number,
        bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
        amount=bill.grand_total,
        taxable_amount=bill.taxable_amount,
        tax_amount=bill.tax_amount,
        is_printed="Yes",
        printed_time=str(datetime.now().time().strftime("%I:%M %p")),
        entered_by=bill.agent_name,
        printed_by=bill.agent_name,
        is_realtime="No",
        sync_with_ird="No",
        payment_method=bill.payment_mode,
        vat_refund_amount=0.0,
        transaction_id="-",
    )

    b = TblSalesEntry(
        bill_date=bill.transaction_date.strftime('%Y-%m-%d'),
        customer_name=bill.customer_name,
        customer_pan=bill.customer_tax_number,
        amount=bill.grand_total,
        NoTaxSales=bill.grand_total - bill.tax_amount -bill.taxable_amount,
        ZeroTaxSales=0.0,
        taxable_amount=bill.taxable_amount,
        tax_amount=bill.tax_amount,
        miti=str(bill.transaction_miti),
        ServicedItem="Others",  # only difference from the rental version ("Goods")
        quantity=1.0,
        bill_no=bill.invoice_number,
        excise_duty_amount=bill.excise_duty_amount,
        fiscal_year=bill.fiscal_year,
        ird_synced=True,
    )

    if bill.tax_amount == 0:
        a.exemptedSales = bill.sub_total
        b.exemptedSales = bill.sub_total

    if bill.payment_mode.lower().strip() == "complimentary":
        try:
            create_journal_for_complimentary(bill)
        except Exception:
            pass
    else:
        try:
            create_journal_for_other_bill(bill)
        except Exception:
            pass

    b.save()
    a.save()


from decimal import Decimal
from accounting.models import AccountSubLedger, AccountSubLedgerTracking


def create_journal_for_rental_bill(instance):
    """
    Same structure as create_journal_for_other_bill, EXCEPT the Sales credit
    line is routed through a 'Rental' subledger under the Sales ledger, so
    rental revenue is distinguishable from regular product sales and Others
    revenue in reports, while the Sales ledger's total_value stays
    consistent with the rest of the books.
    """
    payment_mode = instance.payment_mode.lower().strip()

    grand_total = Decimal(instance.grand_total)
    tax_amount = Decimal(instance.tax_amount)
    discount_amount = Decimal(instance.discount_amount)
    invoice_number = instance.invoice_number
    entry_date = instance.transaction_date_time

    sale_ledger = AccountLedger.objects.get(ledger_name='Sales')

    # Get-or-create the 'Rental' subledger under Sales.
    rental_subledger, _ = AccountSubLedger.objects.get_or_create(
        sub_ledger_name='Rental',
        ledger=sale_ledger,
        defaults={'is_editable': True},
    )

    journal_entry = TblJournalEntry.objects.create(
        employee_name=f'{instance.agent_name}',
        journal_total=(grand_total - discount_amount),
        entry_date=entry_date,
        bill_id=instance.id,
        narration=f'Created Automatically during Rental bill from bill no {invoice_number}',
    )

    if discount_amount > 0:
        discount_expenses = AccountLedger.objects.get(ledger_name__iexact='Discount Expenses')
        discount_sales = AccountLedger.objects.get(ledger_name__iexact='Discount Sales')

        TblDrJournalEntry.objects.create(
            particulars="Discount Expenses A/C Dr.", debit_amount=discount_amount,
            journal_entry=journal_entry, ledger=discount_expenses
        )
        TblCrJournalEntry.objects.create(
            particulars="To Discount Sales", credit_amount=discount_amount,
            journal_entry=journal_entry, ledger=discount_sales
        )

        discount_expenses.total_value += discount_amount
        discount_expenses.save()
        update_cumulative_ledger_bill(discount_expenses, entry_date, journal_entry)

        discount_sales.total_value += discount_amount
        discount_sales.save()
        update_cumulative_ledger_bill(discount_sales, entry_date, journal_entry)

    if tax_amount > 0:
        vat_payable = AccountLedger.objects.get(ledger_name='VAT Payable')
        vat_payable.total_value += tax_amount
        vat_payable.save()
        update_cumulative_ledger_bill(vat_payable, entry_date, journal_entry)

        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To VAT Payable",
            ledger=vat_payable, credit_amount=tax_amount
        )

    if payment_mode == 'credit':
        account_chart = AccountChart.objects.get(group='Sundry Debtors')
        try:
            dr_ledger = AccountLedger.objects.get(
                ledger_name=f'{instance.customer.pk} - {instance.customer.name}'
            )
            dr_ledger.total_value += grand_total
            dr_ledger.save()
            update_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)
        except AccountLedger.DoesNotExist:
            dr_ledger = AccountLedger.objects.create(
                ledger_name=f'{instance.customer.pk} - {instance.customer.name}',
                account_chart=account_chart, total_value=grand_total
            )
            create_cumulative_ledger_bill(dr_ledger, entry_date, journal_entry)

        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars=f"{instance.customer.name} A/C Dr",
            ledger=dr_ledger, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Rental",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=rental_subledger,
        )

    elif payment_mode == "credit card":
        card_transaction_ledger = AccountLedger.objects.get(ledger_name='Card Transactions')
        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="Card Transaction A/C Dr",
            ledger=card_transaction_ledger, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Rental",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=rental_subledger,
        )
        card_transaction_ledger.total_value += grand_total
        card_transaction_ledger.save()
        update_cumulative_ledger_bill(card_transaction_ledger, entry_date, journal_entry)

    elif payment_mode == "mobile payment":
        mobile_payment = AccountLedger.objects.get(ledger_name='Mobile Payments')
        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="Mobile Payment A/C Dr",
            ledger=mobile_payment, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Rental",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=rental_subledger,
        )
        mobile_payment.total_value += grand_total
        mobile_payment.save()
        update_cumulative_ledger_bill(mobile_payment, entry_date, journal_entry)

    elif payment_mode == "cash":
        cash_ledger = AccountLedger.objects.get(ledger_name='Cash-In-Hand')
        cash_ledger.total_value += grand_total
        cash_ledger.save()
        update_cumulative_ledger_bill(cash_ledger, entry_date, journal_entry)

        TblDrJournalEntry.objects.create(
            journal_entry=journal_entry,
            particulars=f"Rental bill invoice {invoice_number} Cash A/C Dr",
            ledger=cash_ledger, debit_amount=grand_total
        )
        TblCrJournalEntry.objects.create(
            journal_entry=journal_entry, particulars="To Sales - Rental",
            ledger=sale_ledger, credit_amount=(grand_total - tax_amount),
            sub_ledger=rental_subledger,
        )

    # ---- Update Sales ledger total (same as create_journal_for_bill) ----
    sale_ledger.total_value += (grand_total - tax_amount)
    sale_ledger.save()
    update_cumulative_ledger_bill(sale_ledger, entry_date, journal_entry)

    # ---- Track the subledger movement ----
    prev_value = rental_subledger.total_value
    subledger_tracking = AccountSubLedgerTracking.objects.create(
        subledger=rental_subledger, prev_amount=prev_value, journal=journal_entry
    )
    rental_subledger.total_value += (grand_total - tax_amount)
    rental_subledger.save()
    subledger_tracking.new_amount = rental_subledger.total_value
    subledger_tracking.value_changed = rental_subledger.total_value - prev_value
    subledger_tracking.save()

from nepali_datetime import date as nepali_date

def build_sales_entry_ird_payload(entry, is_realtime):
    from bill.models import  IrdCredentials
    ird_creds = IrdCredentials.objects.first()
    if not ird_creds:
        return None

    ad_date = datetime.strptime(entry.bill_date, '%Y-%m-%d').date()
    bs = nepali_date.from_datetime_date(ad_date)

    try:
        exempted = float(entry.exemptedSales or 0)
    except (TypeError, ValueError):
        exempted = 0

    return {
        "username": ird_creds.username,
        "password": ird_creds.password,
        "seller_pan": ird_creds.seller_pan,
        "buyer_pan": entry.customer_pan or "0",
        "fiscal_year": entry.fiscal_year,
        "buyer_name": entry.customer_name or "Walk-in Customer",
        "invoice_number": str(entry.bill_no),
        "invoice_date": f"{bs.year}.{bs.month:02d}.{bs.day:02d}",
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
        "tax_exempted_sales": exempted,
        "isrealtime": is_realtime,
        "datetimeClient": datetime.now().isoformat(),
    }


def attempt_hotel_ird_sync(entry_id):
    from bill.models import TblSalesEntry, TblTaxEntry
    from bill.ird.postbillintoird import postbillintoird

    entry = TblSalesEntry.objects.get(pk=entry_id)
    if entry.ird_synced is not False:      # already synced, or not an IRD-tracked entry
        return entry.ird_synced

    entry.ird_last_attempt_at = timezone.now()
    is_first_attempt = entry.ird_retry_count == 0
    fields = ['ird_synced', 'ird_sync_error', 'ird_last_attempt_at', 'ird_retry_count', 'ird_response']

    try:
        payload = build_sales_entry_ird_payload(entry, is_realtime=is_first_attempt)
        if payload is None:
            entry.ird_synced = None          # no IRD credentials: nothing to retry
            entry.ird_sync_error = "No IRD credentials configured"
            entry.save(update_fields=fields)
            return None

        raw_response = postbillintoird(payload)
        response_body = raw_response[0] if isinstance(raw_response, tuple) else raw_response

        if isinstance(response_body, dict):
            ird_code = response_body.get('code') or response_body.get('Code')
        else:
            ird_code = response_body
        try:
            ird_code = int(ird_code)
        except (TypeError, ValueError):
            ird_code = None

        if ird_code in (200, 101):
            with db_transaction.atomic():
                entry.ird_synced = True
                entry.ird_sync_error = None if ird_code == 200 else "IRD reported bill already exists (code 101) -- treated as synced"
                entry.ird_response = str(response_body)
                entry.save(update_fields=fields)
                TblTaxEntry.objects.filter(
                    bill_no=entry.bill_no, fiscal_year=entry.fiscal_year
                ).update(sync_with_ird="Yes", is_realtime="Yes" if is_first_attempt else "No")
            return True

        meaning = IRD_CODE_MEANINGS.get(ird_code, "Unrecognized response")
        raise Exception(f"IRD code {ird_code} ({meaning}): {response_body}")

    except Exception as e:
        entry.ird_synced = False
        entry.ird_sync_error = str(e)
        entry.ird_retry_count += 1
        try:
            entry.save(update_fields=fields)
        except Exception as save_error:
            logging.getLogger(__name__).error(
                f"Failed to persist IRD sync failure for sales entry {entry_id}: {save_error} (original error: {e})"
            )
        return False


_hotel_sweep_lock = threading.Lock()

from datetime import timedelta
from django.db.models import Q
def sync_pending_hotel_ird(limit=5, max_retries=10, cooldown_minutes=2, exclude_ids=None):
    """
    Opportunistic retry of hotel sales entries that failed to sync with IRD.
    Called after a hotel bill syncs successfully, so IRD is known to be reachable.
    Returns how many entries were synced.
    """
    from bill.models import TblSalesEntry

    # one sweep at a time per process
    if not _hotel_sweep_lock.acquire(blocking=False):
        return 0
    try:
        cutoff = timezone.now() - timedelta(minutes=cooldown_minutes)
        pending = (
            TblSalesEntry.objects
            .filter(ird_synced=False, ird_retry_count__lt=max_retries)
            .filter(Q(ird_last_attempt_at__isnull=True) | Q(ird_last_attempt_at__lt=cutoff))
            .exclude(pk__in=exclude_ids or [])
            .order_by('pk')[:limit]
        )

        synced = 0
        for e in pending:
            result = attempt_hotel_ird_sync(e.pk)
            if result is True:
                synced += 1
            elif result is False:
                break        # IRD started failing mid-sweep, stop hammering it
        return synced
    finally:
        _hotel_sweep_lock.release()