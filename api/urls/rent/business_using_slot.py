# urls.py
from rest_framework.routers import DefaultRouter
from api.views.rent.business_using_slot import BusinessViewSet, BusinessExcelUploadView

from django.urls import path

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')

urlpatterns = router.urls


urlpatterns += [
    path('business/bulk-upload/', BusinessExcelUploadView.as_view(), name='business-bulk-upload'),
]