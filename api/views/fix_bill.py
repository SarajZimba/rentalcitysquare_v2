from rest_framework.views import APIView
from rest_framework.response import Response
from bill.models import Bill, TblSalesEntry
from datetime import datetime
class FixBillApiView(APIView):
    def post(self, request, *args, **kwargs):
        incorrect_bills = request.data

        print(incorrect_bills)
        for data in incorrect_bills:
            # Update bills for the given date range
            transaction_date_str = data.get('transaction_date')
            # transaction_date = datetime.strptime(transaction_date_str, '%b. %d, %Y').date()
            transaction_date = parse_date(transaction_date_str)
            invoice_number = data.get('invoice_number')
            try:
                bill = Bill.objects.get(transaction_date=transaction_date, invoice_number=invoice_number,status=True)
            except Exception as e:
                return Response({"error":str(e)}, 400)
            bill.amount_in_words = convert_to_words(bill.grand_total)
            billdateinstring = transaction_date.strftime("%Y-%m-%d")
            salesentry = TblSalesEntry.objects.get(bill_date=billdateinstring, bill_no=invoice_number)
            salesentry.amount = bill.grand_total
            salesentry.taxable_amount = bill.taxable_amount
            salesentry.tax_amount = bill.tax_amount
            salesentry.save()
            bill.save()  

        return Response({"details": "Bill corrected successfully"}, 200)          



from num2words import num2words

def convert_to_words(grand_total):
    # Convert the integer part (before the decimal) into words
    integer_part = int(grand_total)  # The rupees part
    integer_words = num2words(integer_part, lang='en').upper()  # Convert to words and make uppercase
    
    # Remove commas from the words output
    integer_words = integer_words.replace(",", "")
    
    # Convert the decimal part (paisa) if it exists
    decimal_part = grand_total - integer_part  # This is the paisa part
    paisa_words = ""

    if decimal_part > 0:
        # Round paisa to two decimal places, then multiply by 100 to get paisa
        paisa_value = round(decimal_part * 100)  # e.g., 0.62 becomes 62 paisa
        paisa_words = num2words(paisa_value, lang='en').upper()  # Convert paisa to words and make uppercase
        # Remove commas from paisa words
        paisa_words = paisa_words.replace(",", "")
        amount_in_words = f"{integer_words} RUPEES AND {paisa_words} PAISA ONLY"
    else:
        amount_in_words = f"{integer_words} RUPEES ONLY"
    
    return amount_in_words

from datetime import datetime

def parse_date(date_str):
    formats = [
        '%B %d, %Y',  # "March 19, 2025"
        '%b. %d, %Y',  # "Mar. 19, 2025"
        # add other formats as needed
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date '{date_str}' doesn't match any expected format")