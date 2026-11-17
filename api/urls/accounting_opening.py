from api.views.accounting_opening import AccountChartBulkImportAPI, OpeningCountAPIView

from django.urls import path

urlpatterns = [
    path('accountchart/bulk-import/', AccountChartBulkImportAPI.as_view(), name='accountchart_bulk_import'),
    path('ledgers/<int:ledger_id>/opening-count/', OpeningCountAPIView.as_view(), name='accountledger_opening'),
]