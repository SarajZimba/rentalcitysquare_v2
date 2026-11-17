# purchase/utils.py

import decimal
from django.db import transaction
from django.db.models import Q, F
from decimal import Decimal
from django.shortcuts import get_object_or_404

from accounting.models import (
    AccountSubLedger, AccountSubLedgerTracking, TblJournalEntry, 
    TblCrJournalEntry, TblDrJournalEntry, CumulativeLedger, AccountLedger
)
from purchase.models import ProductPurchase


@transaction.atomic()
def soft_delete_journal_purchase(journal_id, purchase=None):
    """
    Completely delete a purchase journal and reverse all accounting effects.
    
    Args:
        journal_id: ID of the journal entry to delete
        purchase: Optional Purchase object (needed for product subledger reversal)
    
    Returns:
        bool: True if successful
    """
    try:
        # Get journal entry
        journal_entry = get_object_or_404(TblJournalEntry, id=journal_id)
        
        # 1. Reverse main ledger balances
        _reverse_ledger_balances(journal_entry)
        
        # 2. Reverse product subledgers (if purchase provided)
        if purchase:
            _reverse_product_subledgers(purchase)
        
        # 3. Reverse payment mode subledgers
        _reverse_payment_subledgers(journal_entry)
        
        # 4. Remove cumulative ledger entries and update subsequent ones
        _remove_cumulative_ledger_entries(journal_entry)
        
        # 5. Delete all journal records
        _cleanup_journal_records(journal_entry)
        
        return True
        
    except TblJournalEntry.DoesNotExist:
        print(f"Journal Entry {journal_id} not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise  # Re-raise to trigger rollback


def _reverse_ledger_balances(journal_entry):
    """Reverse main ledger balances."""
    
    # Reverse credit entries
    for credit_entry in TblCrJournalEntry.objects.filter(journal_entry=journal_entry):
        ledger = credit_entry.ledger
        amount = credit_entry.credit_amount
        account_type = ledger.account_chart.account_type
        
        if account_type in ['Asset', 'Expense']:
            # Credit decreased Asset/Expense → add back
            ledger.total_value += amount
        elif account_type in ['Liability', 'Revenue', 'Equity']:
            # Credit increased Liability/Revenue → subtract
            ledger.total_value -= amount
        
        ledger.save()
    
    # Reverse debit entries
    for debit_entry in TblDrJournalEntry.objects.filter(journal_entry=journal_entry):
        ledger = debit_entry.ledger
        amount = debit_entry.debit_amount
        account_type = ledger.account_chart.account_type
        
        if account_type in ['Asset', 'Expense']:
            # Debit increased Asset/Expense → subtract
            ledger.total_value -= amount
        elif account_type in ['Liability', 'Revenue', 'Equity']:
            # Debit decreased Liability/Revenue → add back
            ledger.total_value += amount
        
        ledger.save()


def _reverse_product_subledgers(purchase):
    """Reverse per-product subledgers."""
    product_purchases = ProductPurchase.objects.filter(
        purchase=purchase
    ).select_related('product', 'product__category', 'product__ledger')
    
    for pp in product_purchases:
        product = pp.product
        debit_account = product.ledger
        
        if not debit_account:
            continue
        
        subledgername = f'{product.title} ({product.category.title}) - Purchase'
        item_total = Decimal(str(pp.item_total))
        
        try:
            sub = AccountSubLedger.objects.get(
                sub_ledger_name=subledgername, 
                ledger=debit_account
            )
            sub.total_value -= item_total
            sub.save()
        except AccountSubLedger.DoesNotExist:
            continue


def _reverse_payment_subledgers(journal_entry):
    """Reverse payment-mode subledgers."""
    # Get all subledger tracking records linked to this journal
    trackings = AccountSubLedgerTracking.objects.filter(journal=journal_entry)
    
    for tracking in trackings:
        subledger = tracking.subledger
        if subledger:
            # Reverse the change
            subledger.total_value -= tracking.value_changed
            subledger.save()


def _remove_cumulative_ledger_entries(journal_entry):
    """
    Remove cumulative ledger entries and update subsequent entries.
    """
    # Get all cumulative entries for this journal
    cumulative_entries = CumulativeLedger.objects.filter(journal=journal_entry)
    
    for entry in cumulative_entries:
        ledger = entry.ledger
        value_changed = entry.value_changed
        
        # Update ALL subsequent cumulative entries for this ledger
        subsequent_entries = CumulativeLedger.objects.filter(
            ledger=ledger,
            id__gt=entry.id
        ).order_by('id')
        
        # Adjust each subsequent entry
        for subsequent in subsequent_entries:
            subsequent.total_value -= value_changed
            subsequent.save()
        
        # Now delete this cumulative entry
        entry.delete()


def _cleanup_journal_records(journal_entry):
    """Delete all journal-related records."""
    # Delete subledger tracking records
    AccountSubLedgerTracking.objects.filter(journal=journal_entry).delete()
    
    # Delete debit and credit entries
    TblDrJournalEntry.objects.filter(journal_entry=journal_entry).delete()
    TblCrJournalEntry.objects.filter(journal_entry=journal_entry).delete()
    
    # Delete the journal entry itself
    journal_entry.delete()


# ============================================
# OPTIMIZED VERSION (Better Performance)
# ============================================

@transaction.atomic()
def soft_delete_journal_purchase_optimized(journal_id, purchase=None):
    """
    Optimized version with bulk operations.
    """
    try:
        journal_entry = get_object_or_404(TblJournalEntry, id=journal_id)
        
        # Get all records in one go
        debit_entries = list(TblDrJournalEntry.objects.filter(journal_entry=journal_entry))
        credit_entries = list(TblCrJournalEntry.objects.filter(journal_entry=journal_entry))
        cumulative_entries = list(CumulativeLedger.objects.filter(journal=journal_entry))
        
        # 1. Reverse ledger balances using bulk operations
        _reverse_ledger_balances_bulk(debit_entries, credit_entries)
        
        # 2. Reverse product subledgers
        if purchase:
            _reverse_product_subledgers_bulk(purchase)
        
        # 3. Reverse payment subledgers
        _reverse_payment_subledgers_bulk(journal_entry)
        
        # 4. Remove cumulative entries with bulk update
        _remove_cumulative_entries_bulk(cumulative_entries)
        
        # 5. Clean up all records
        AccountSubLedgerTracking.objects.filter(journal=journal_entry).delete()
        TblDrJournalEntry.objects.filter(journal_entry=journal_entry).delete()
        TblCrJournalEntry.objects.filter(journal_entry=journal_entry).delete()
        journal_entry.delete()
        
        return True
        
    except TblJournalEntry.DoesNotExist:
        print(f"Journal Entry {journal_id} not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


def _reverse_ledger_balances_bulk(debit_entries, credit_entries):
    """Reverse ledger balances using bulk operations."""
    
    # Collect all ledger updates
    ledger_updates = {}
    
    # Process credit entries
    for credit in credit_entries:
        ledger = credit.ledger
        amount = credit.credit_amount
        account_type = ledger.account_chart.account_type
        
        if ledger.id not in ledger_updates:
            ledger_updates[ledger.id] = {'ledger': ledger, 'delta': Decimal('0.00')}
        
        if account_type in ['Asset', 'Expense']:
            ledger_updates[ledger.id]['delta'] += amount
        else:
            ledger_updates[ledger.id]['delta'] -= amount
    
    # Process debit entries
    for debit in debit_entries:
        ledger = debit.ledger
        amount = debit.debit_amount
        account_type = ledger.account_chart.account_type
        
        if ledger.id not in ledger_updates:
            ledger_updates[ledger.id] = {'ledger': ledger, 'delta': Decimal('0.00')}
        
        if account_type in ['Asset', 'Expense']:
            ledger_updates[ledger.id]['delta'] -= amount
        else:
            ledger_updates[ledger.id]['delta'] += amount
    
    # Bulk update ledgers
    for ledger_data in ledger_updates.values():
        ledger = ledger_data['ledger']
        delta = ledger_data['delta']
        if delta != 0:
            ledger.total_value = F('total_value') + delta
            ledger.save()
            ledger.refresh_from_db()


def _reverse_product_subledgers_bulk(purchase):
    """Reverse product subledgers using bulk operations."""
    product_purchases = ProductPurchase.objects.filter(
        purchase=purchase
    ).select_related('product', 'product__ledger', 'product__category')
    
    subledger_updates = {}
    
    for pp in product_purchases:
        product = pp.product
        debit_account = product.ledger
        
        if not debit_account:
            continue
        
        subledgername = f'{product.title} ({product.category.title}) - Purchase'
        item_total = Decimal(str(pp.item_total))
        
        try:
            sub = AccountSubLedger.objects.get(
                sub_ledger_name=subledgername, 
                ledger=debit_account
            )
            if sub.id not in subledger_updates:
                subledger_updates[sub.id] = {'subledger': sub, 'delta': Decimal('0.00')}
            subledger_updates[sub.id]['delta'] -= item_total
        except AccountSubLedger.DoesNotExist:
            continue
    
    # Bulk update subledgers
    for sub_data in subledger_updates.values():
        subledger = sub_data['subledger']
        delta = sub_data['delta']
        if delta != 0:
            subledger.total_value = F('total_value') + delta
            subledger.save()
            subledger.refresh_from_db()


def _reverse_payment_subledgers_bulk(journal_entry):
    """Reverse payment subledgers using bulk operations."""
    trackings = AccountSubLedgerTracking.objects.filter(journal=journal_entry)
    
    subledger_updates = {}
    
    for tracking in trackings:
        subledger = tracking.subledger
        if subledger:
            if subledger.id not in subledger_updates:
                subledger_updates[subledger.id] = {'subledger': subledger, 'delta': Decimal('0.00')}
            subledger_updates[subledger.id]['delta'] -= tracking.value_changed
    
    # Bulk update subledgers
    for sub_data in subledger_updates.values():
        subledger = sub_data['subledger']
        delta = sub_data['delta']
        if delta != 0:
            subledger.total_value = F('total_value') + delta
            subledger.save()
            subledger.refresh_from_db()


def _remove_cumulative_entries_bulk(cumulative_entries):
    """Remove cumulative entries with bulk operations."""
    # Group by ledger
    entries_by_ledger = {}
    
    for entry in cumulative_entries:
        ledger_id = entry.ledger_id
        if ledger_id not in entries_by_ledger:
            entries_by_ledger[ledger_id] = []
        entries_by_ledger[ledger_id].append(entry)
    
    # Process each ledger
    for ledger_id, entries in entries_by_ledger.items():
        # Sort entries by ID (creation order)
        entries.sort(key=lambda x: x.id)
        
        # For each entry, update subsequent entries
        for entry in entries:
            value_changed = entry.value_changed
            
            # Get the next entries (using the entry's ID as reference)
            next_entries = CumulativeLedger.objects.filter(
                ledger_id=ledger_id,
                id__gt=entry.id
            )
            
            if next_entries.exists():
                # Bulk update all subsequent entries
                next_entries.update(total_value=F('total_value') - value_changed)
        
        # Delete all entries for this ledger
        entry_ids = [e.id for e in entries]
        CumulativeLedger.objects.filter(id__in=entry_ids).delete()