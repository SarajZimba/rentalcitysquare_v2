# urls.py
from django.urls import path
from api.views.hotel.givehotelbillnumber import HotelBillIndexAPIView

urlpatterns = [
    path('givehotelbillnumber/', HotelBillIndexAPIView.as_view(), name='givehotelbillnumber'),
]