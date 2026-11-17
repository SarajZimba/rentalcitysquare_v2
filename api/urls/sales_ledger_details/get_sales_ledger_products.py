from api.views.sales_ledger_details.get_sales_ledger_products import LedgerProductBreakdownAPIView


from django.urls import path

urlpatterns = [
    path("get_sales_ledger_products/", LedgerProductBreakdownAPIView.as_view(), name="get_sales_ledger_products")

]
