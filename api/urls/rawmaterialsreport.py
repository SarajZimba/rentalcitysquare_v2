from api.views.rawmaterialsreport import RawMaterialsReportView
from django.urls import path

urlpatterns = []

urlpatterns += [
    path('rawmaterialsreport/', RawMaterialsReportView.as_view(), name='rawmaterialsreport'),
]