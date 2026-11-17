# import requests


# def postbillintoird(cbms_payload):
#         # # 6️⃣ Post to IRD CBMS

#         cbms_url = "https://cbapi.ird.gov.np/api/bill"
#         headers = {"Content-Type": "application/json"}
#         r = requests.post(cbms_url, json=cbms_payload, headers=headers, timeout=10)

#         if r.status_code == 200:
#             print( f"BIll {cbms_payload} posted successfully into ird {r.text}")
#         else:
#             print( "CBMS API failed",r.text)
#             return {"success": "", "cbms_error": r.text}, 400

        # pass

# bill/ird/postbillintoird.py  (add these alongside your existing postbillintoird())


import requests

def postbillintoird(cbms_payload):
    cbms_url = "https://cbapi.ird.gov.np/api/bill"
    headers = {"Content-Type": "application/json"}
    r = requests.post(cbms_url, json=cbms_payload, headers=headers, timeout=10)
    print(r)
    print(r.status_code)
    if r.status_code == 200:
        print(f"BIll {cbms_payload} posted successfully into ird {r.text}")
        return {"code": r.text, "raw": r.text}, 200
    else:
        print("CBMS API failed", r.text)
        return {"success": "", "cbms_error": r.text}, 400

from datetime import datetime
from nepali_datetime import date as nepali_date

from bill.models import IrdCredentials


def build_bill_ird_payload(bill):
    """
    Build the IRD payload from a Bill instance that already has FINAL totals
    (grand_total, tax_amount, taxable_amount) set. Safe to call for both
    sale and rental bills, as long as it's called after totals are finalized.
    """
    ird_creds = IrdCredentials.objects.first()
    if not ird_creds:
        return None

    ad_date = bill.transaction_date
    # transaction_date is a DateField for Bill, but the signal used
    # instance.transaction_date.date() because at that point it was still
    # a datetime from auto_now_add on a slightly different flow -- adjust
    # this line if you hit an AttributeError either way.
    if hasattr(ad_date, "date"):
        ad_date = ad_date.date()
    bs_date = nepali_date.from_datetime_date(ad_date)
    bs_date_str = f"{bs_date.year}.{bs_date.month:02d}.{bs_date.day:02d}"

    return {
        "username": ird_creds.username,
        "password": ird_creds.password,
        "seller_pan": ird_creds.seller_pan,
        "buyer_pan": bill.customer_tax_number or "0",
        "fiscal_year": bill.fiscal_year,
        "buyer_name": bill.customer_name,
        "invoice_number": f"{bill.invoice_number}",
        "invoice_date": bs_date_str,
        "total_sales": float(bill.grand_total),
        "taxable_sales_vat": float(bill.grand_total) - float(bill.tax_amount),
        "vat": float(bill.tax_amount),
        "excisable_amount": 0,
        "excise": 0,
        "taxable_sales_hst": 0,
        "hst": 0,
        "amount_for_esf": 0,
        "esf": 0,
        "export_sales": 0,
        "tax_exempted_sales": 0,
        "isrealtime": True,
        "datetimeClient": datetime.now().isoformat(),
    }


# def post_bill_to_ird(bill):
#     """
#     Build the payload from a bill with FINAL totals and post it to IRD.
#     Raises on failure so the caller can decide whether to roll back
#     (e.g. inside an outer transaction.atomic()).
#     Returns None if there are no IRD credentials configured (skip, not fail).
#     """
#     from .postbillintoird import postbillintoird  # your existing low-level caller

#     payload = build_bill_ird_payload(bill)
#     if payload is None:
#         print(f"No IRD credentials found, skipping IRD post for bill {bill.invoice_number}.")
#         return None

#     print(payload)
#     return postbillintoird(payload)
