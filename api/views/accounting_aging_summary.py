from datetime import date, timedelta
from decimal import Decimal

from django.views import View
from django.shortcuts import render

from accounting.models import AccountLedger, CumulativeLedger, TblDrJournalEntry, TblCrJournalEntry


class SundryDebtorsAgingSummaryView(View):
    template_name = 'accounting/sundry_debtors_aging.html'

    def get(self, request):
        # Aging is always calculated as of today — no date filter accepted
        # from the frontend for this report.
        as_of_date = date.today()

        # credit_days: payment terms in days. An invoice isn't "overdue" until
        # entry_date + credit_days has passed. Default 0 = due immediately,
        # so "Current" bucket = invoices dated today (0 days overdue).
        credit_days = int(request.GET.get('creditDays', 0))

        sundry_debtors_ledgers = AccountLedger.objects.filter(
            account_chart__group="Sundry Debtors"
        )

        bucket_labels = ['current', '1_30', '31_60', '61_90', 'over_90']

        ledger_details = []
        grand_totals = {b: Decimal('0') for b in bucket_labels}
        grand_totals['total'] = Decimal('0')

        for ledger in sundry_debtors_ledgers:
            remaining_debits = []

            # --- Opening balance: exactly one is_opening=True row per ledger.
            # Pulled from CumulativeLedger (not ledger.opening_count directly)
            # because that's where the real, backdated entry_date lives —
            # set by EditOpeningCountView.
            opening_row = CumulativeLedger.objects.filter(
                ledger=ledger,
                is_opening=True,
                entry_date__date__lte=as_of_date
            ).first()

            if opening_row:
                net_amt = Decimal(str(opening_row.debit_amount)) - Decimal(str(opening_row.credit_amount))
                if net_amt > 0:
                    remaining_debits.append({
                        'amount': net_amt,
                        'entry_date': opening_row.entry_date.date(),
                    })

            # --- Regular debit entries (invoices) up to today
            debit_entries = list(
                TblDrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__entry_date__lte=as_of_date
                ).order_by('journal_entry__entry_date', 'id')
                .values('debit_amount', 'journal_entry__entry_date')
            )
            for d in debit_entries:
                remaining_debits.append({
                    'amount': Decimal(str(d['debit_amount'])),
                    'entry_date': d['journal_entry__entry_date'],
                })

            if not remaining_debits:
                continue

            # Sort combined debits (opening balance + invoices) chronologically
            # so FIFO credit-matching below applies to the truly oldest first.
            remaining_debits.sort(key=lambda x: x['entry_date'])

            # --- Credit entries (payments) up to today, oldest first
            credit_entries = list(
                TblCrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__entry_date__lte=as_of_date
                ).order_by('journal_entry__entry_date', 'id')
                .values_list('credit_amount', flat=True)
            )

            # Apply credits FIFO against the oldest remaining debit balances first.
            total_credit = sum(Decimal(str(c)) for c in credit_entries)
            idx = 0
            while total_credit > 0 and idx < len(remaining_debits):
                applied = min(remaining_debits[idx]['amount'], total_credit)
                remaining_debits[idx]['amount'] -= applied
                total_credit -= applied
                if remaining_debits[idx]['amount'] == 0:
                    idx += 1
                else:
                    break

            # Bucket whatever's left (i.e. still unpaid) by age from today.
            buckets = {b: Decimal('0') for b in bucket_labels}
            for d in remaining_debits:
                if d['amount'] <= 0:
                    continue
                due_date = d['entry_date'] + timedelta(days=credit_days)
                days_overdue = (as_of_date - due_date).days

                if days_overdue <= 0:
                    buckets['current'] += d['amount']
                elif days_overdue <= 30:
                    buckets['1_30'] += d['amount']
                elif days_overdue <= 60:
                    buckets['31_60'] += d['amount']
                elif days_overdue <= 90:
                    buckets['61_90'] += d['amount']
                else:
                    buckets['over_90'] += d['amount']

            row_total = sum(buckets.values())
            if row_total == 0:
                continue

            ledger_details.append({
                'ledger_id': ledger.id,
                'ledger_name': ledger.ledger_name,
                'current': buckets['current'],
                '1_30': buckets['1_30'],
                '31_60': buckets['31_60'],
                '61_90': buckets['61_90'],
                'over_90': buckets['over_90'],
                'total': row_total,
            })

            for b in bucket_labels:
                grand_totals[b] += buckets[b]
            grand_totals['total'] += row_total

        return render(request, self.template_name, {
            'ledger_details': ledger_details,
            'grand_totals': grand_totals,
            'as_of_date': as_of_date,
            'credit_days': credit_days,
        })




class SundryCreditorsAgingSummaryView(View):
    template_name = 'accounting/sundry_creditors_aging.html'

    def get(self, request):
        # Aging is always calculated as of today — no date filter accepted
        # from the frontend for this report.
        as_of_date = date.today()

        # credit_days: payment terms in days. A bill isn't "overdue" until
        # entry_date + credit_days has passed. Default 0 = due immediately,
        # so "Current" bucket = bills dated today (0 days overdue).
        credit_days = int(request.GET.get('creditDays', 0))

        sundry_creditors_ledgers = AccountLedger.objects.filter(
            account_chart__group="Sundry Creditors"
        )

        bucket_labels = ['current', '1_30', '31_60', '61_90', 'over_90']

        ledger_details = []
        grand_totals = {b: Decimal('0') for b in bucket_labels}
        grand_totals['total'] = Decimal('0')

        for ledger in sundry_creditors_ledgers:
            # For creditors, the "invoice" side is CREDIT entries (bills we
            # owe), and the "payment" side is DEBIT entries (money we paid
            # out to settle them) — the reverse of the debtors direction.
            remaining_credits = []

            # --- Opening balance: exactly one is_opening=True row per ledger.
            # Pulled from CumulativeLedger for its real, backdated entry_date
            # (set by EditOpeningCountView), not from ledger.opening_count.
            opening_row = CumulativeLedger.objects.filter(
                ledger=ledger,
                is_opening=True,
                entry_date__date__lte=as_of_date
            ).first()

            if opening_row:
                # Net payable from the opening row: credit (owed) minus debit
                # (already paid at opening).
                net_amt = Decimal(str(opening_row.credit_amount)) - Decimal(str(opening_row.debit_amount))
                if net_amt > 0:
                    remaining_credits.append({
                        'amount': net_amt,
                        'entry_date': opening_row.entry_date.date(),
                    })

            # --- Regular credit entries (bills owed) up to today
            credit_entries_qs = list(
                TblCrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__entry_date__lte=as_of_date
                ).order_by('journal_entry__entry_date', 'id')
                .values('credit_amount', 'journal_entry__entry_date')
            )
            for c in credit_entries_qs:
                remaining_credits.append({
                    'amount': Decimal(str(c['credit_amount'])),
                    'entry_date': c['journal_entry__entry_date'],
                })

            if not remaining_credits:
                continue

            # Sort combined credits (opening balance + bills) chronologically
            # so FIFO payment-matching below applies to the oldest bill first.
            remaining_credits.sort(key=lambda x: x['entry_date'])

            # --- Debit entries (payments made) up to today, oldest first
            debit_entries_qs = list(
                TblDrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__entry_date__lte=as_of_date
                ).order_by('journal_entry__entry_date', 'id')
                .values_list('debit_amount', flat=True)
            )

            # Apply payments FIFO against the oldest remaining bill balances first.
            total_debit = sum(Decimal(str(d)) for d in debit_entries_qs)
            idx = 0
            while total_debit > 0 and idx < len(remaining_credits):
                applied = min(remaining_credits[idx]['amount'], total_debit)
                remaining_credits[idx]['amount'] -= applied
                total_debit -= applied
                if remaining_credits[idx]['amount'] == 0:
                    idx += 1
                else:
                    break

            # Bucket whatever's left (i.e. still unpaid) by age from today.
            buckets = {b: Decimal('0') for b in bucket_labels}
            for c in remaining_credits:
                if c['amount'] <= 0:
                    continue
                due_date = c['entry_date'] + timedelta(days=credit_days)
                days_overdue = (as_of_date - due_date).days

                if days_overdue <= 0:
                    buckets['current'] += c['amount']
                elif days_overdue <= 30:
                    buckets['1_30'] += c['amount']
                elif days_overdue <= 60:
                    buckets['31_60'] += c['amount']
                elif days_overdue <= 90:
                    buckets['61_90'] += c['amount']
                else:
                    buckets['over_90'] += c['amount']

            row_total = sum(buckets.values())
            if row_total == 0:
                continue

            ledger_details.append({
                'ledger_id': ledger.id,
                'ledger_name': ledger.ledger_name,
                'current': buckets['current'],
                '1_30': buckets['1_30'],
                '31_60': buckets['31_60'],
                '61_90': buckets['61_90'],
                'over_90': buckets['over_90'],
                'total': row_total,
            })

            for b in bucket_labels:
                grand_totals[b] += buckets[b]
            grand_totals['total'] += row_total

        return render(request, self.template_name, {
            'ledger_details': ledger_details,
            'grand_totals': grand_totals,
            'as_of_date': as_of_date,
            'credit_days': credit_days,
        })


from datetime import date
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# class SundryDebtorsReceivableSummaryAPI(APIView):

#     def get(self, request):
#         # Everything is calculated as of today.
#         as_of_date = date.today()

#         sundry_debtors_ledgers = AccountLedger.objects.filter(
#             account_chart__group="Sundry Debtors"
#         )

#         bucket_labels = ['1_30', '31_60', '61_90', 'over_90']

#         ledger_details = []
#         grand_totals = {
#             'current': Decimal('0'),
#             '1_30': Decimal('0'),
#             '31_60': Decimal('0'),
#             '61_90': Decimal('0'),
#             'over_90': Decimal('0'),
#             'total': Decimal('0'),
#         }

#         for ledger in sundry_debtors_ledgers:
#             # --- Opening balance: exactly one is_opening=True row per ledger,
#             # pulled from CumulativeLedger for its real entry_date (set by
#             # EditOpeningCountView), not from ledger.opening_count directly.
#             opening_row = CumulativeLedger.objects.filter(
#                 ledger=ledger,
#                 is_opening=True,
#                 entry_date__date__lte=as_of_date
#             ).first()

#             opening_balance = Decimal('0')
#             if opening_row:
#                 opening_balance = Decimal(str(opening_row.debit_amount)) - Decimal(str(opening_row.credit_amount))

#             # --- All debit entries (invoices) up to today, all-time total.
#             debit_entries = TblDrJournalEntry.objects.filter(
#                 ledger=ledger,
#                 journal_entry__entry_date__lte=as_of_date
#             )
#             total_debit = sum(Decimal(str(d)) for d in debit_entries.values_list('debit_amount', flat=True))

#             # --- All credit entries (payments received) up to today.
#             # Pulled with entry_date so each individual payment can be bucketed
#             # by how long ago it was received.
#             credit_entries = list(
#                 TblCrJournalEntry.objects.filter(
#                     ledger=ledger,
#                     journal_entry__entry_date__lte=as_of_date
#                 ).values('credit_amount', 'journal_entry__entry_date')
#             )
#             total_credit = sum(Decimal(str(c['credit_amount'])) for c in credit_entries)

#             if not credit_entries and total_debit == 0 and opening_balance == 0:
#                 continue

#             # "Current" = total outstanding balance owed to us as of today —
#             # NOT an aging bucket here, just opening + all debits - all credits.
#             current_balance = opening_balance + total_debit - total_credit

#             # Day-range columns = payments actually received, bucketed by how
#             # many days ago each payment came in (relative to today).
#             buckets = {b: Decimal('0') for b in bucket_labels}
#             for c in credit_entries:
#                 amount = Decimal(str(c['credit_amount']))
#                 entry_date = c['journal_entry__entry_date']
#                 if not entry_date:
#                     continue
#                 days_ago = (as_of_date - entry_date).days

#                 if days_ago <= 30:
#                     buckets['1_30'] += amount
#                 elif days_ago <= 60:
#                     buckets['31_60'] += amount
#                 elif days_ago <= 90:
#                     buckets['61_90'] += amount
#                 else:
#                     buckets['over_90'] += amount

#             row_total = current_balance + sum(buckets.values())

#             if current_balance == 0 and row_total == 0:
#                 continue

#             ledger_details.append({
#                 'ledger_id': ledger.id,
#                 'ledger_name': ledger.ledger_name,
#                 'current': str(current_balance),
#                 '1_30': str(buckets['1_30']),
#                 '31_60': str(buckets['31_60']),
#                 '61_90': str(buckets['61_90']),
#                 'over_90': str(buckets['over_90']),
#                 'total': str(row_total),
#             })

#             grand_totals['current'] += current_balance
#             for b in bucket_labels:
#                 grand_totals[b] += buckets[b]
#             grand_totals['total'] += row_total

#         return Response({
#             'as_of_date': as_of_date,
#             'ledger_details': ledger_details,
#             'grand_totals': {k: str(v) for k, v in grand_totals.items()},
#         }, status=status.HTTP_200_OK)


# class SundryCreditorsPayableSummaryAPI(APIView):

#     def get(self, request):
#         # Everything is calculated as of today.
#         as_of_date = date.today()

#         sundry_creditors_ledgers = AccountLedger.objects.filter(
#             account_chart__group="Sundry Creditors"
#         )

#         bucket_labels = ['1_30', '31_60', '61_90', 'over_90']

#         ledger_details = []
#         grand_totals = {
#             'current': Decimal('0'),
#             '1_30': Decimal('0'),
#             '31_60': Decimal('0'),
#             '61_90': Decimal('0'),
#             'over_90': Decimal('0'),
#             'total': Decimal('0'),
#         }

#         for ledger in sundry_creditors_ledgers:
#             # --- Opening balance: exactly one is_opening=True row per ledger,
#             # pulled from CumulativeLedger for its real entry_date (set by
#             # EditOpeningCountView), not from ledger.opening_count directly.
#             opening_row = CumulativeLedger.objects.filter(
#                 ledger=ledger,
#                 is_opening=True,
#                 entry_date__date__lte=as_of_date
#             ).first()

#             opening_balance = Decimal('0')
#             if opening_row:
#                 # For creditors, opening payable = credit (owed) - debit (already paid).
#                 opening_balance = Decimal(str(opening_row.credit_amount)) - Decimal(str(opening_row.debit_amount))

#             # --- All credit entries (bills owed to suppliers) up to today, all-time total.
#             credit_entries = TblCrJournalEntry.objects.filter(
#                 ledger=ledger,
#                 journal_entry__entry_date__lte=as_of_date
#             )
#             total_credit = sum(Decimal(str(c)) for c in credit_entries.values_list('credit_amount', flat=True))

#             # --- All debit entries (payments we made to suppliers) up to today.
#             # Pulled with entry_date so each individual payment can be bucketed
#             # by how long ago it was made.
#             debit_entries = list(
#                 TblDrJournalEntry.objects.filter(
#                     ledger=ledger,
#                     journal_entry__entry_date__lte=as_of_date
#                 ).values('debit_amount', 'journal_entry__entry_date')
#             )
#             total_debit = sum(Decimal(str(d['debit_amount'])) for d in debit_entries)

#             if not debit_entries and total_credit == 0 and opening_balance == 0:
#                 continue

#             # "Current" = total outstanding balance we still owe as of today —
#             # NOT an aging bucket here, just opening + all credits - all debits.
#             current_balance = opening_balance + total_credit - total_debit

#             # Day-range columns = payments we actually made, bucketed by how
#             # many days ago each payment went out (relative to today).
#             buckets = {b: Decimal('0') for b in bucket_labels}
#             for d in debit_entries:
#                 amount = Decimal(str(d['debit_amount']))
#                 entry_date = d['journal_entry__entry_date']
#                 if not entry_date:
#                     continue
#                 days_ago = (as_of_date - entry_date).days

#                 if days_ago <= 30:
#                     buckets['1_30'] += amount
#                 elif days_ago <= 60:
#                     buckets['31_60'] += amount
#                 elif days_ago <= 90:
#                     buckets['61_90'] += amount
#                 else:
#                     buckets['over_90'] += amount

#             row_total = current_balance + sum(buckets.values())

#             if current_balance == 0 and row_total == 0:
#                 continue

#             ledger_details.append({
#                 'ledger_id': ledger.id,
#                 'ledger_name': ledger.ledger_name,
#                 'current': str(current_balance),
#                 '1_30': str(buckets['1_30']),
#                 '31_60': str(buckets['31_60']),
#                 '61_90': str(buckets['61_90']),
#                 'over_90': str(buckets['over_90']),
#                 'total': str(row_total),
#             })

#             grand_totals['current'] += current_balance
#             for b in bucket_labels:
#                 grand_totals[b] += buckets[b]
#             grand_totals['total'] += row_total

#         return Response({
#             'as_of_date': as_of_date,
#             'ledger_details': ledger_details,
#             'grand_totals': {k: str(v) for k, v in grand_totals.items()},
#         }, status=status.HTTP_200_OK)


class SundryDebtorsReceivableSummaryAPI(APIView):

    def get(self, request):
        # Everything is calculated as of today.
        as_of_date = date.today()

        branch_id = request.GET.get('branch')
        if not branch_id:
            return Response(
                {'error': 'branch is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sundry_debtors_ledgers = AccountLedger.objects.filter(
            account_chart__group="Sundry Debtors",
            branch_id=branch_id
        )

        bucket_labels = ['1_30', '31_60', '61_90', 'over_90']

        ledger_details = []
        grand_totals = {
            'current': Decimal('0'),
            '1_30': Decimal('0'),
            '31_60': Decimal('0'),
            '61_90': Decimal('0'),
            'over_90': Decimal('0'),
            'total': Decimal('0'),
        }

        for ledger in sundry_debtors_ledgers:
            # --- Opening balance: exactly one is_opening=True row per ledger,
            # pulled from CumulativeLedger for its real entry_date (set by
            # EditOpeningCountView), not from ledger.opening_count directly.
            # Also scoped to the same branch, since CumulativeLedger carries
            # its own branch FK.
            opening_row = CumulativeLedger.objects.filter(
                ledger=ledger,
                is_opening=True,
                branch_id=branch_id,
                entry_date__date__lte=as_of_date
            ).first()

            opening_balance = Decimal('0')
            if opening_row:
                opening_balance = Decimal(str(opening_row.debit_amount)) - Decimal(str(opening_row.credit_amount))

            # --- All debit entries (invoices) up to today, all-time total.
            # journal_entry__branch scopes to the branch via TblJournalEntry,
            # as a safeguard in case a ledger's entries ever span branches
            # through paidfrom_ledger cross-postings.
            debit_entries = TblDrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__branch_id=branch_id,
                journal_entry__entry_date__lte=as_of_date
            )
            total_debit = sum(Decimal(str(d)) for d in debit_entries.values_list('debit_amount', flat=True))

            # --- All credit entries (payments received) up to today.
            # Pulled with entry_date so each individual payment can be bucketed
            # by how long ago it was received.
            credit_entries = list(
                TblCrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__branch_id=branch_id,
                    journal_entry__entry_date__lte=as_of_date
                ).values('credit_amount', 'journal_entry__entry_date')
            )
            total_credit = sum(Decimal(str(c['credit_amount'])) for c in credit_entries)

            if not credit_entries and total_debit == 0 and opening_balance == 0:
                continue

            # "Current" = total outstanding balance owed to us as of today —
            # NOT an aging bucket here, just opening + all debits - all credits.
            current_balance = opening_balance + total_debit - total_credit

            # Day-range columns = payments actually received, bucketed by how
            # many days ago each payment came in (relative to today).
            buckets = {b: Decimal('0') for b in bucket_labels}
            for c in credit_entries:
                amount = Decimal(str(c['credit_amount']))
                entry_date = c['journal_entry__entry_date']
                if not entry_date:
                    continue
                days_ago = (as_of_date - entry_date).days

                if days_ago <= 30:
                    buckets['1_30'] += amount
                elif days_ago <= 60:
                    buckets['31_60'] += amount
                elif days_ago <= 90:
                    buckets['61_90'] += amount
                else:
                    buckets['over_90'] += amount

            row_total = current_balance + sum(buckets.values())

            if current_balance == 0 and row_total == 0:
                continue

            ledger_details.append({
                'ledger_id': ledger.id,
                'ledger_name': ledger.ledger_name,
                'current': str(current_balance),
                '1_30': str(buckets['1_30']),
                '31_60': str(buckets['31_60']),
                '61_90': str(buckets['61_90']),
                'over_90': str(buckets['over_90']),
                'total': str(row_total),
            })

            grand_totals['current'] += current_balance
            for b in bucket_labels:
                grand_totals[b] += buckets[b]
            grand_totals['total'] += row_total

        return Response({
            'branch': branch_id,
            'as_of_date': as_of_date,
            'ledger_details': ledger_details,
            'grand_totals': {k: str(v) for k, v in grand_totals.items()},
        }, status=status.HTTP_200_OK)


class SundryCreditorsPayableSummaryAPI(APIView):

    def get(self, request):
        # Everything is calculated as of today.
        as_of_date = date.today()

        branch_id = request.GET.get('branch')
        if not branch_id:
            return Response(
                {'error': 'branch is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sundry_creditors_ledgers = AccountLedger.objects.filter(
            account_chart__group="Sundry Creditors",
            branch_id=branch_id
        )

        bucket_labels = ['1_30', '31_60', '61_90', 'over_90']

        ledger_details = []
        grand_totals = {
            'current': Decimal('0'),
            '1_30': Decimal('0'),
            '31_60': Decimal('0'),
            '61_90': Decimal('0'),
            'over_90': Decimal('0'),
            'total': Decimal('0'),
        }

        for ledger in sundry_creditors_ledgers:
            # --- Opening balance: exactly one is_opening=True row per ledger,
            # pulled from CumulativeLedger for its real entry_date (set by
            # EditOpeningCountView), not from ledger.opening_count directly.
            # Also scoped to the same branch, since CumulativeLedger carries
            # its own branch FK.
            opening_row = CumulativeLedger.objects.filter(
                ledger=ledger,
                is_opening=True,
                branch_id=branch_id,
                entry_date__date__lte=as_of_date
            ).first()

            opening_balance = Decimal('0')
            if opening_row:
                # For creditors, opening payable = credit (owed) - debit (already paid).
                opening_balance = Decimal(str(opening_row.credit_amount)) - Decimal(str(opening_row.debit_amount))

            # --- All credit entries (bills owed to suppliers) up to today, all-time total.
            # journal_entry__branch scopes to the branch via TblJournalEntry,
            # as a safeguard in case a ledger's entries ever span branches
            # through paidfrom_ledger cross-postings.
            credit_entries = TblCrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__branch_id=branch_id,
                journal_entry__entry_date__lte=as_of_date
            )
            total_credit = sum(Decimal(str(c)) for c in credit_entries.values_list('credit_amount', flat=True))

            # --- All debit entries (payments we made to suppliers) up to today.
            # Pulled with entry_date so each individual payment can be bucketed
            # by how long ago it was made.
            debit_entries = list(
                TblDrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__branch_id=branch_id,
                    journal_entry__entry_date__lte=as_of_date
                ).values('debit_amount', 'journal_entry__entry_date')
            )
            total_debit = sum(Decimal(str(d['debit_amount'])) for d in debit_entries)

            if not debit_entries and total_credit == 0 and opening_balance == 0:
                continue

            # "Current" = total outstanding balance we still owe as of today —
            # NOT an aging bucket here, just opening + all credits - all debits.
            current_balance = opening_balance + total_credit - total_debit

            # Day-range columns = payments we actually made, bucketed by how
            # many days ago each payment went out (relative to today).
            buckets = {b: Decimal('0') for b in bucket_labels}
            for d in debit_entries:
                amount = Decimal(str(d['debit_amount']))
                entry_date = d['journal_entry__entry_date']
                if not entry_date:
                    continue
                days_ago = (as_of_date - entry_date).days

                if days_ago <= 30:
                    buckets['1_30'] += amount
                elif days_ago <= 60:
                    buckets['31_60'] += amount
                elif days_ago <= 90:
                    buckets['61_90'] += amount
                else:
                    buckets['over_90'] += amount

            row_total = current_balance + sum(buckets.values())

            if current_balance == 0 and row_total == 0:
                continue

            ledger_details.append({
                'ledger_id': ledger.id,
                'ledger_name': ledger.ledger_name,
                'current': str(current_balance),
                '1_30': str(buckets['1_30']),
                '31_60': str(buckets['31_60']),
                '61_90': str(buckets['61_90']),
                'over_90': str(buckets['over_90']),
                'total': str(row_total),
            })

            grand_totals['current'] += current_balance
            for b in bucket_labels:
                grand_totals[b] += buckets[b]
            grand_totals['total'] += row_total

        return Response({
            'branch': branch_id,
            'as_of_date': as_of_date,
            'ledger_details': ledger_details,
            'grand_totals': {k: str(v) for k, v in grand_totals.items()},
        }, status=status.HTTP_200_OK)

from django.db.models import Sum
class SundryDebtorsAgingSummaryAPI(APIView):

    def get(self, request):
        as_of_date = date.today()


        sundry_debtors_ledgers = AccountLedger.objects.filter(
            account_chart__group="Sundry Debtors"
        )

        bucket_labels = ['1_30', '31_60', '61_90', 'over_90']

        ledger_details = []
        grand_totals = {b: Decimal('0') for b in bucket_labels}
        grand_totals['total'] = Decimal('0')

        for ledger in sundry_debtors_ledgers:
            # --- Opening balance, treated as the earliest "invoice" for
            # aging purposes, dated at its own entry_date.
            opening_row = CumulativeLedger.objects.filter(
                ledger=ledger,
                is_opening=True,
                entry_date__date__lte=as_of_date
            ).first()

            opening_balance = Decimal('0')
            opening_date = None
            if opening_row:
                opening_balance = Decimal(str(opening_row.debit_amount)) - Decimal(str(opening_row.credit_amount))
                opening_date = opening_row.entry_date.date() if hasattr(opening_row.entry_date, 'date') else opening_row.entry_date

            # --- All debit entries (invoices), oldest first — needed in
            # order for FIFO matching against payments below.
            debit_entries = list(
                TblDrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__entry_date__lte=as_of_date
                ).values('debit_amount', 'journal_entry__entry_date')
                .order_by('journal_entry__entry_date')
            )

            # --- Total payments received, all-time. FIFO doesn't care when
            # each payment came in, only how much total credit exists to
            # apply against the oldest outstanding invoices first.
            total_credit = TblCrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__entry_date__lte=as_of_date
            ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')
            total_credit = Decimal(str(total_credit))

            # --- Build the invoice list in date order: opening balance
            # first (if positive), then each debit entry.
            invoices = []
            if opening_balance > 0 and opening_date:
                invoices.append({'date': opening_date, 'amount': opening_balance})
            for d in debit_entries:
                amt = Decimal(str(d['debit_amount']))
                entry_date = d['journal_entry__entry_date']
                if amt > 0 and entry_date:
                    invoices.append({'date': entry_date, 'amount': amt})

            if not invoices:
                continue

            # --- FIFO: apply total payments against oldest invoices first,
            # leaving each invoice's still-unpaid remainder.
            remaining_credit = total_credit
            outstanding_invoices = []
            for inv in invoices:
                if remaining_credit >= inv['amount']:
                    remaining_credit -= inv['amount']
                    continue  # fully paid off, nothing outstanding
                outstanding_amount = inv['amount'] - remaining_credit
                remaining_credit = Decimal('0')
                outstanding_invoices.append({'date': inv['date'], 'amount': outstanding_amount})

            if not outstanding_invoices:
                continue

            # --- Bucket each outstanding invoice by its own age.
            buckets = {b: Decimal('0') for b in bucket_labels}
            for inv in outstanding_invoices:
                days_ago = (as_of_date - inv['date']).days
                if days_ago <= 30:
                    buckets['1_30'] += inv['amount']
                elif days_ago <= 60:
                    buckets['31_60'] += inv['amount']
                elif days_ago <= 90:
                    buckets['61_90'] += inv['amount']
                else:
                    buckets['over_90'] += inv['amount']

            row_total = sum(buckets.values())
            if row_total == 0:
                continue

            ledger_details.append({
                'ledger_id': ledger.id,
                'ledger_name': ledger.ledger_name,
                '1_30': str(buckets['1_30']),
                '31_60': str(buckets['31_60']),
                '61_90': str(buckets['61_90']),
                'over_90': str(buckets['over_90']),
                'total': str(row_total),
            })

            for b in bucket_labels:
                grand_totals[b] += buckets[b]
            grand_totals['total'] += row_total

        return Response({
            'as_of_date': as_of_date,
            'ledger_details': ledger_details,
            'grand_totals': {k: str(v) for k, v in grand_totals.items()},
        }, status=status.HTTP_200_OK)


from django.db.models import Sum

class SundryCreditorsAgingSummaryAPI(APIView):

    def get(self, request):
        as_of_date = date.today()


        sundry_creditors_ledgers = AccountLedger.objects.filter(
            account_chart__group="Sundry Creditors"
        )

        bucket_labels = ['1_30', '31_60', '61_90', 'over_90']

        ledger_details = []
        grand_totals = {b: Decimal('0') for b in bucket_labels}
        grand_totals['total'] = Decimal('0')

        for ledger in sundry_creditors_ledgers:
            # --- Opening balance, treated as the earliest "bill" for
            # aging purposes, dated at its own entry_date.
            # For creditors, opening payable = credit (owed) - debit (already paid).
            opening_row = CumulativeLedger.objects.filter(
                ledger=ledger,
                is_opening=True,
                entry_date__date__lte=as_of_date
            ).first()

            opening_balance = Decimal('0')
            opening_date = None
            if opening_row:
                opening_balance = Decimal(str(opening_row.credit_amount)) - Decimal(str(opening_row.debit_amount))
                opening_date = opening_row.entry_date.date() if hasattr(opening_row.entry_date, 'date') else opening_row.entry_date

            # --- All credit entries (bills owed to suppliers), oldest first —
            # needed in order for FIFO matching against payments below.
            credit_entries = list(
                TblCrJournalEntry.objects.filter(
                    ledger=ledger,
                    journal_entry__entry_date__lte=as_of_date
                ).values('credit_amount', 'journal_entry__entry_date')
                .order_by('journal_entry__entry_date')
            )

            # --- Total payments we made, all-time. FIFO doesn't care when
            # each payment went out, only how much total debit exists to
            # apply against the oldest outstanding bills first.
            total_debit = TblDrJournalEntry.objects.filter(
                ledger=ledger,
                journal_entry__entry_date__lte=as_of_date
            ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')
            total_debit = Decimal(str(total_debit))

            # --- Build the bill list in date order: opening balance first
            # (if positive), then each credit entry.
            bills = []
            if opening_balance > 0 and opening_date:
                bills.append({'date': opening_date, 'amount': opening_balance})
            for c in credit_entries:
                amt = Decimal(str(c['credit_amount']))
                entry_date = c['journal_entry__entry_date']
                if amt > 0 and entry_date:
                    bills.append({'date': entry_date, 'amount': amt})

            if not bills:
                continue

            # --- FIFO: apply total payments against oldest bills first,
            # leaving each bill's still-unpaid remainder.
            remaining_debit = total_debit
            outstanding_bills = []
            for bill in bills:
                if remaining_debit >= bill['amount']:
                    remaining_debit -= bill['amount']
                    continue  # fully paid off, nothing outstanding
                outstanding_amount = bill['amount'] - remaining_debit
                remaining_debit = Decimal('0')
                outstanding_bills.append({'date': bill['date'], 'amount': outstanding_amount})

            if not outstanding_bills:
                continue

            # --- Bucket each outstanding bill by its own age.
            buckets = {b: Decimal('0') for b in bucket_labels}
            for bill in outstanding_bills:
                days_ago = (as_of_date - bill['date']).days
                if days_ago <= 30:
                    buckets['1_30'] += bill['amount']
                elif days_ago <= 60:
                    buckets['31_60'] += bill['amount']
                elif days_ago <= 90:
                    buckets['61_90'] += bill['amount']
                else:
                    buckets['over_90'] += bill['amount']

            row_total = sum(buckets.values())
            if row_total == 0:
                continue

            ledger_details.append({
                'ledger_id': ledger.id,
                'ledger_name': ledger.ledger_name,
                '1_30': str(buckets['1_30']),
                '31_60': str(buckets['31_60']),
                '61_90': str(buckets['61_90']),
                'over_90': str(buckets['over_90']),
                'total': str(row_total),
            })

            for b in bucket_labels:
                grand_totals[b] += buckets[b]
            grand_totals['total'] += row_total

        return Response({
            'as_of_date': as_of_date,
            'ledger_details': ledger_details,
            'grand_totals': {k: str(v) for k, v in grand_totals.items()},
        }, status=status.HTTP_200_OK)