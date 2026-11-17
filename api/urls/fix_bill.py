from django.urls import path
from api.views.fix_bill import FixBillApiView


urlpatterns = [
    path('fixincorrectbills', FixBillApiView.as_view(), name='fix-incorrect-bills-salesentry')
]