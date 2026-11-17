# urls.py
from django.urls import path
from api.views.rent.combined_bill import CombinedRentalAndOtherBillListAPIView

urlpatterns = [
    path('bills/rental-and-other/', CombinedRentalAndOtherBillListAPIView.as_view(), name='combined-rental-other-bill-list'),
]
