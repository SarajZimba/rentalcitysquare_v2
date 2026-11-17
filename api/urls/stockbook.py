from api.views.stockbook import StockBookSummaryAPI
from django.urls import path

urlpatterns = []

urlpatterns += [
    path('stockbookreport/', StockBookSummaryAPI.as_view(), name='stockbookreport'),
]