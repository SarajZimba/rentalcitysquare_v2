from ..views.accounting import update_account_type ,update_account_group, update_account_ledger, update_account_subledger,\
    ChartOfAccountAPIView, JournalEntryAPIView, TrialBalanceAPIView, ProfitAndLossAPIView, BalanceSheetAPIView, get_depreciation_pool,\
    LedgersAPIView, SubLedgersAPI, SundryLedgersAPI, ExpenseSubLedgersAPI, AccountChartListAPI, AccountChartCreateAPI, AccountLedgerCreateAPI, AccountSubLedgerCreateAPI, LedgerWithSubLedgersCreateAPI, AccountLedgerWithSubledgersAPIView, TrialBalanceLedgerAPIView, LedgerDetailAPIView, SubLedgerCashflowAPIView

from django.urls import path

urlpatterns = [
    path("update-account-type/<int:pk>/", update_account_type, name="update_account_type"),
    path("update-account-group/<int:pk>/", update_account_group, name="update_account_group"),
    path("update-account-ledger/<int:pk>/", update_account_ledger, name="update_account_ledger"),
    path("update-account-subledger/<int:pk>/", update_account_subledger, name="update_account_subledger"),
    path("get-depreciation-pool/", get_depreciation_pool),



    path('accounting/chart-of-accounts/', ChartOfAccountAPIView.as_view(), name="chart_of_account_list"),
    path('accounting/journal-entry/', JournalEntryAPIView.as_view(), name="journal_entry_list"),
    path('accounting/trial-balance/', TrialBalanceAPIView.as_view(), name="trial_balance_list"),
    path('accounting/trial-balance/v2', TrialBalanceLedgerAPIView.as_view(), name="trial_balance_list_v2"),
    path('accounting/profit-and-loss/', ProfitAndLossAPIView.as_view(), name="profit_and_loss_list"),
    path('accounting/balance-sheet/', BalanceSheetAPIView.as_view(), name="balance_sheet_list"),
    path('get-ledgers', LedgersAPIView.as_view(), name="ledgers=list" ),

    path('get-subledgers/', SubLedgersAPI.as_view(), name="subledgers-list"),
    path('get-expense-subledgers/', ExpenseSubLedgersAPI.as_view(), name="expense-subledgers-list"),

    path('get-sundryledgers/', SundryLedgersAPI.as_view(), name = 'sundryledgers-list' ),
    path('accountledger-subledgers/', AccountLedgerWithSubledgersAPIView.as_view(), name = 'accountledger-subledgers' )


]


urlpatterns += [
    # ... your existing patterns
    path('accountchart/list/', AccountChartListAPI.as_view(), name='accountchart_list_api'),
    path('accountchart/create/', AccountChartCreateAPI.as_view(), name='accountchart_create_api'),
]

urlpatterns += [
    path('accountledger/create/', AccountLedgerCreateAPI.as_view(), name='accountledger_create_api'),
]


urlpatterns += [
    path('accountsubledger/create/', AccountSubLedgerCreateAPI.as_view(), name='accountsubledger_create_api'),

    path('ledger-with-subledgers/create/', LedgerWithSubLedgersCreateAPI.as_view()),

    path('ledgercrdrdetail/<int:ledger_id>/', LedgerDetailAPIView.as_view(), name= 'ledgercrdrdetail'),

    path('subledger-cashflow/', SubLedgerCashflowAPIView.as_view(), name='subledger-cashflow-api'),
]

