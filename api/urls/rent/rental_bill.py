# urls.py
from django.urls import path
from api.views.rent.rental_bill import BusinessRentalBillCreateAPIView, RentalBillDetailAPIView

urlpatterns = [

    path('rental-bills/create/', BusinessRentalBillCreateAPIView.as_view(), name='rental-bill-create'),
    path('rental-bills/detail/', RentalBillDetailAPIView.as_view(), name='rental-bill-detail'),
]