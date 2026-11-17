


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.journal_entry import HOTEL_BILL_TERMINAL


def peek_terminal_bill_no(terminal=HOTEL_BILL_TERMINAL):
    """Return the next bill number for the terminal WITHOUT advancing the acounter."""
    from bill.models import BillIndex
    Branch = BillIndex._meta.get_field('branch').related_model
    branch = Branch.objects.first()          # only one branch for now

    index = BillIndex.objects.filter(terminal=terminal, branch=branch).first()

    bill_number = str(branch.branch_code) + "-" + str(terminal) + "-" + str(index.bill_index) if index else str(branch.branch_code) + "-" + str(terminal) + "-" + "1"
    return bill_number

class HotelBillIndexAPIView(APIView):
    """
    GET /api/hotel-bill-index/
    -> {"terminal": "2", "next_bill_no": 15}
    """
    permission_classes = [IsAuthenticated]

    from organization.models import Organization

    org = Organization.objects.first()

    fiscal_year = org.get_fiscal_year()

    def get(self, request):
        return Response({
            "terminal": HOTEL_BILL_TERMINAL,
            "next_bill_no": peek_terminal_bill_no(),
            "fiscal_year": self.fiscal_year
        })