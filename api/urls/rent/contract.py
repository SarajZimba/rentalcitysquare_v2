# urls.py
from rest_framework.routers import DefaultRouter
from api.views.rent.contract import ContractViewSet, BusinessSlotsAPIView

from django.urls import path

router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')

urlpatterns = router.urls


urlpatterns += [
    path('business/<int:business_id>/slots/', BusinessSlotsAPIView.as_view(), name='business-slots'),
]