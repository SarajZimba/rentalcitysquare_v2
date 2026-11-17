# PurchaseCreateAPI

# urls.py
from django.urls import path
from api.views.purchase import PurchaseCreateAPI



from api.views.purchase import PurchaseCreateAPI
urlpatterns = []

urlpatterns += [
    path('purchase-create-from-bill/', PurchaseCreateAPI.as_view(), name='produced-and-bom'),
]
