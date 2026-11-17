from api.views.productionitemreport import ProducedItemReportView
from django.urls import path

urlpatterns = []

urlpatterns += [
    path('produceditemreport/', ProducedItemReportView.as_view(), name='produced-item-report'),
]