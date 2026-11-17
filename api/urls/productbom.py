# urls.py
from django.urls import path
from api.views.productbom import ProductBOMCreateView, ProductBOMBulkCreateView, ProductBOMReportView, AllProductBOMReportView

urlpatterns = [
    path('bom/create/', ProductBOMCreateView.as_view()),  # Single entry
    path('bom/bulk-create/', ProductBOMBulkCreateView.as_view()),  # Bulk insert
]
    
urlpatterns += [
    path('bom/report/<int:product_id>/', ProductBOMReportView.as_view(), name='bom-report'),
    path('bom/allreport/', AllProductBOMReportView.as_view(), name='bom-report'),
]


from api.views.productbom import CreateProductionLogView,BulkCreateProductionLogView

urlpatterns += [
    path('production-log/', CreateProductionLogView.as_view(), name='create-production-log'),
    path('production-log/bulk-create/', BulkCreateProductionLogView.as_view(), name='bulk-create-production-log'),

]


from api.views.productbom import ProductionLogReportView

urlpatterns += [
    path("production-log/<int:log_id>/report/", ProductionLogReportView.as_view(), name="production-log-report")
]


from api.views.productbom import ProductionSummaryReportView

urlpatterns += [
    path('production-log/report/', ProductionSummaryReportView.as_view(), name='production-summary-report'),
]

from api.views.productbom import ProductBOMDeleteView

urlpatterns += [
    path("delete-bom/<int:pk>/", ProductBOMDeleteView.as_view(), name="delete-bom"),
]

from django.urls import path
from api.views.productbom import DeleteProductionLogView  # adjust import as needed

urlpatterns += [
    path('delete-production-log/<int:pk>/', DeleteProductionLogView.as_view(), name='delete-production-log'),
]

from api.views.productbom import VerifyToken

urlpatterns += [
    path('verify-token/', VerifyToken.as_view(), name='verify-token'),
]

from django.urls import path
from api.views.productbom import ProductOpeningStockBulkCreateView  # Adjust path

urlpatterns += [
    path('opening-stock/bulk-create/', ProductOpeningStockBulkCreateView.as_view(), name='bulk-create-opening-stock'),
]

from api.views.productbom import ProducedProductsAndItsBom

urlpatterns += [
    path('producedanditsbom/allreport/', ProducedProductsAndItsBom.as_view(), name='produced-and-bom'),
]
