# # urls.py
# from django.urls import path
# from api.views.estimated_bill import EstimatedBillCreateView

# urlpatterns = [
#     path("estimated-bills/", EstimatedBillCreateView.as_view(), name="estimated-bill-create"),
# ]

# urls.py
from django.urls import path
from api.views.estimated_bill import (
    EstimatedBillCreateView,
    EstimatedBillListView,
    EstimatedBillDetailView,
)

urlpatterns = [
    path("estimated-bills/", EstimatedBillCreateView.as_view(), name="estimated-bill-create"),
    path("estimated-bills/list/", EstimatedBillListView.as_view(), name="estimated-bill-list"),
    path("estimated-bills/<int:pk>/", EstimatedBillDetailView.as_view(), name="estimated-bill-detail"),
]