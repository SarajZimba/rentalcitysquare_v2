# views.py
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from bill.models import EstimatedBill
from api.serializers.estimated_bill import EstimatedBillCreateSerializer, EstimatedBillOutputSerializer
from rest_framework.permissions import IsAuthenticated

class EstimatedBillCreateView(CreateAPIView):
    queryset = EstimatedBill.objects.all()
    serializer_class = EstimatedBillCreateSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bill = serializer.save()

        output = EstimatedBillOutputSerializer(bill)
        return Response(output.data, status=status.HTTP_201_CREATED)


# views.py (add below EstimatedBillCreateView)

from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.exceptions import NotFound

from bill.models import EstimatedBill
from api.serializers.estimated_bill import (
    EstimatedBillCreateSerializer,
    EstimatedBillUpdateSerializer,
    EstimatedBillOutputSerializer,
)


class EstimatedBillListView(ListAPIView):
    queryset = EstimatedBill.objects.all().prefetch_related("items")
    serializer_class = EstimatedBillOutputSerializer
    permission_classes = [IsAuthenticated]


class EstimatedBillDetailView(RetrieveUpdateDestroyAPIView):
    queryset = EstimatedBill.objects.all().prefetch_related("items")
    lookup_field = "pk"
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return EstimatedBillUpdateSerializer
        return EstimatedBillOutputSerializer

    def get_object(self):
        try:
            return super().get_object()
        except EstimatedBill.DoesNotExist:
            raise NotFound("Estimated bill not found.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", request.method == "PATCH")
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        bill = serializer.save()

        output = EstimatedBillOutputSerializer(bill)
        return Response(output.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
