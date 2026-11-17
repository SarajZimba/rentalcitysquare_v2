# from api.views.accounting_opening import AccountChartBulkImportAPI

from django.urls import path

from api.views.accounting_aging_summary import SundryDebtorsAgingSummaryView, SundryCreditorsAgingSummaryView, SundryDebtorsReceivableSummaryAPI, SundryCreditorsPayableSummaryAPI, SundryDebtorsAgingSummaryAPI, SundryCreditorsAgingSummaryAPI

urlpatterns = [
path('sundry_debtors_aging/', SundryDebtorsAgingSummaryAPI.as_view(), name='sundry_debtors_aging'),
path('sundry_creditors_aging/', SundryCreditorsAgingSummaryAPI.as_view(), name='sundry_creditors_aging'),
path('sundry_debtors_receivable_summary/', SundryDebtorsReceivableSummaryAPI.as_view(), name='sundry_debtors_receivable_summary'),
path('sundry_creditors_payable_summary/', SundryCreditorsPayableSummaryAPI.as_view(), name='sundry_creditors_payable_summary'),
]