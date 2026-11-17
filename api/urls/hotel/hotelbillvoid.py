

# urls.py
from django.urls import path
from api.views.hotel.hotelbillvoid import HotelBillVoidAPIView

urlpatterns = [
    path('hotelbillvoid/', HotelBillVoidAPIView.as_view(), name='hotelbillvoid'),
]