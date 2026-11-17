from .user import urlpatterns as user_urlpatterns
from .product import urlpatterns as product_urlpatterns
from .bill import urlpatterns as bill_urlpatterns
from .organization import urlpatterns as org_urlpatterns
from .discount_urls import urlpatterns as discount_urlspatterns
from .purchaserequisition_api import urlpatterns as purchaserequisition_urlpattern
from .accounting_urls import urlpatterns as accounting_urlpatterns
from .mobilepayment_type import urlpatterns as mobile_urlpatterns
from .endday_report import urlpatterns as enddayreport_urlpatterns
from .today_report import urlpatterns as todayreport_urlpatterns
from .category_wise_report import urlpatterns as category_wise_sale_urlpatterns
from .report import urlpatterns as report_urlpatterns 
from.master import urlpatterns as master_urlpatterns
from .bill_todayid import urlpatterns as bill_todayid_urlpatterns
from .productbom import urlpatterns as product_bom_urlpatterns
from .productionitemreport import urlpatterns as productionitemreport_urlpatterns
from .rawmaterialsreport import urlpatterns as rawmaterialsreport_urlpatterns
from .stockbook import urlpatterns as stockbookreport_urlpatterns
from .journal_entry import urlpatterns as journal_entry_urls
from .credit_journal_entry import urlpatterns as credit_journal_entry_urls
from .give_ledger import urlpatterns as give_ledger_urls
from .accounting_opening import urlpatterns as accounting_opening_urls
from .purchase import urlpatterns as purchase_urlpatterns
from.accounting_aging_summary import urlpatterns as accounting_aging_summary_urlpatterns

from .sales_ledger_details.get_sales_ledger_products import urlpatterns as get_sales_ledger_products_urlpatterns

from .rent.space_slot import urlpatterns as space_slot_urlpatterns
from .rent.business_using_slot import urlpatterns as business_using_slot_urlpatterns
from .rent.contract import urlpatterns as contract_urlpatterns
from .rent.rental_bill import urlpatterns as rental_bill_urlpatterns
from .rent.other_bill import urlpatterns as other_bill_urlpatterns
from .rent.combined_bill import urlpatterns as combined_bill_urlpatterns
from .sso_login import urlpatterns as sso_login_urlpatterns
from .review_logintoken import urlpatterns as review_logintoken_urlpatterns
from .estimated_bill import urlpatterns as estimated_bill_urlpatterns
from .hotel.givehotelbillnumber import urlpatterns as givehotelbillnumber_urlpatterns
from .hotel.hotelbillvoid import urlpatterns as hotelbillvoid_urlpatterns
from .partyledgerpayment import urlpatterns as partyledgerpayment_urlpatterns
urlpatterns = (
    [] + user_urlpatterns + product_urlpatterns + bill_urlpatterns + org_urlpatterns+discount_urlspatterns+purchaserequisition_urlpattern+accounting_urlpatterns+mobile_urlpatterns+enddayreport_urlpatterns+todayreport_urlpatterns+category_wise_sale_urlpatterns +report_urlpatterns+ master_urlpatterns+ bill_todayid_urlpatterns + product_bom_urlpatterns + productionitemreport_urlpatterns + rawmaterialsreport_urlpatterns + stockbookreport_urlpatterns + journal_entry_urls  + credit_journal_entry_urls + give_ledger_urls + accounting_opening_urls + purchase_urlpatterns + accounting_aging_summary_urlpatterns + get_sales_ledger_products_urlpatterns + space_slot_urlpatterns + business_using_slot_urlpatterns + contract_urlpatterns + rental_bill_urlpatterns + other_bill_urlpatterns + combined_bill_urlpatterns + sso_login_urlpatterns+ review_logintoken_urlpatterns + estimated_bill_urlpatterns + givehotelbillnumber_urlpatterns + hotelbillvoid_urlpatterns + partyledgerpayment_urlpatterns
 
)
