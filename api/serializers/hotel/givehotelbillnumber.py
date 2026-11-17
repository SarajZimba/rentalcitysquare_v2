def peek_terminal_bill_no(terminal=HOTEL_BILL_TERMINAL):
    """Return the next bill number for the terminal WITHOUT advancing the counter."""
    from bill.models import BillIndex
    Branch = BillIndex._meta.get_field('branch').related_model
    branch = Branch.objects.first()          # only one branch for now

    index = BillIndex.objects.filter(terminal=terminal, branch=branch).first()
    return index.bill_index if index else 1  # no row yet -> first bill will be 1


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.journal_entry import HOTEL_BILL_TERMINAL, peek_terminal_bill_no


class HotelBillIndexAPIView(APIView):
    """
    GET /api/hotel-bill-index/
    -> {"terminal": "2", "next_bill_no": 15}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "terminal": HOTEL_BILL_TERMINAL,
            "next_bill_no": peek_terminal_bill_no(),
        })