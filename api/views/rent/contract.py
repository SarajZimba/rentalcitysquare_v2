# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rent.models import Contract
from api.serializers.rent.contract import ContractSerializer


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('business', 'slot').all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_slot = old_instance.slot
        old_status = old_instance.status

        instance = serializer.save()

        # If slot changed, vacate the old one
        if old_slot.id != instance.slot.id:
            old_slot.vacate()

        # Sync slot status with contract status
        if instance.status == Contract.StatusChoices.ACTIVE:
            instance.slot.occupy()
        elif instance.status in [Contract.StatusChoices.EXPIRED, Contract.StatusChoices.TERMINATED]:
            instance.slot.vacate()

    def perform_destroy(self, instance):
        # Vacate the slot when contract is deleted
        instance.slot.vacate()
        instance.delete()

# api/views/rent/business_slots.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rent.models import Contract, Business
from api.serializers.rent.contract import BusinessSlotSerializer


class BusinessSlotsAPIView(APIView):
    """
    GET /api/business/<business_id>/slots/
    Optional query param: ?active_only=true  -> only currently active contracts

    Returns all slots (with contract details) associated with a business.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_id):
        if not Business.objects.filter(id=business_id).exists():
            return Response(
                {"error": "Business not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        contracts = Contract.objects.filter(business_id=business_id).select_related('slot')

        active_only = request.query_params.get('active_only', 'false').lower() == 'true'
        if active_only:
            contracts = contracts.filter(status=Contract.StatusChoices.ACTIVE)

        serializer = BusinessSlotSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)