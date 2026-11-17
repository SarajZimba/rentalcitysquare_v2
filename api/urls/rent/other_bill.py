# urls.py
from django.urls import path
from api.views.rent.other_bill import OtherBillCreateAPIView, OtherBillVoidAPIView

urlpatterns = [
    path('other-bills/create/', OtherBillCreateAPIView.as_view(), name='other-bill-create'),
    path('other-bills/void/', OtherBillVoidAPIView.as_view(), name='other-bill-void'),
]

