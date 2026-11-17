from datetime import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model


from django.db import models
from django.dispatch import receiver
from organization.models import Organization, Branch
from product.models import Product, ProductStock
from root.utils import BaseModel
from django.db.models.signals import post_save
from .utils import product_sold, create_journal_for_complimentary, create_journal_for_bill


User = get_user_model()


class TblTaxEntry(models.Model):
    idtbltaxEntry = models.AutoField(primary_key=True)
    fiscal_year = models.CharField(max_length=20)
    bill_no = models.CharField(null=True, max_length=20)
    customer_name = models.CharField(max_length=200, null=True)
    customer_pan = models.CharField(max_length=200, null=True)
    bill_date = models.DateField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_printed = models.CharField(max_length=20, default="Yes")
    is_active = models.CharField(max_length=20, default="Yes")
    printed_time = models.CharField(null=True, max_length=20)
    entered_by = models.CharField(null=True, max_length=20)
    printed_by = models.CharField(null=True, max_length=20)
    is_realtime = models.CharField(max_length=20, default="Yes")
    sync_with_ird = models.CharField(max_length=20, default="Yes")
    payment_method = models.CharField(null=True, max_length=20, default="Cash")
    vat_refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_id = models.CharField(null=True, max_length=20)
    unit = models.CharField(default="-", max_length=20)

    class Meta:
        db_table = "tbltaxentry"

    def __str__(self):
        return f"{self.idtbltaxEntry}- {self.fiscal_year} - {self.bill_no}"


class TblSalesEntry(models.Model):
    tblSalesEntry = models.AutoField(primary_key=True)
    bill_date = models.CharField(null=True, max_length=20)
    bill_no = models.CharField(null=True, max_length=20)
    customer_name = models.CharField(max_length=200, null=True)
    customer_pan = models.CharField(max_length=200, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    NoTaxSales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ZeroTaxSales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    miti = models.CharField(null=True, max_length=20)
    ServicedItem = models.CharField(max_length=20, default="Goods")
    quantity = models.PositiveIntegerField(default=1)
    exemptedSales = models.CharField(default="0", max_length=20)
    export = models.CharField(default="0", max_length=20)
    exportCountry = models.CharField(default="0", max_length=20)
    exportNumber = models.CharField(default="0", max_length=20)
    exportDate = models.CharField(default="0", max_length=20)
    unit = models.CharField(default="-", max_length=20)
    excise_duty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    journal_entry = models.ForeignKey(
        'accounting.TblJournalEntry',      # string reference avoids a circular import
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='sales_entries',
    )

    fiscal_year = models.CharField(max_length=20, null=True, blank=True)

    # IRD sync state. NULL = not applicable (rental/other/sale bills sync via Bill),
    # False = pending or failed, True = synced
    ird_synced = models.BooleanField(null=True, blank=True, default=None)
    ird_sync_error = models.TextField(null=True, blank=True)
    ird_last_attempt_at = models.DateTimeField(null=True, blank=True)
    ird_retry_count = models.PositiveIntegerField(default=0)
    ird_response = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "tblSalesEntry"

    def __str__(self):
        return f"{self.tblSalesEntry}- {self.bill_date} - {self.bill_no}"


class TablReturnEntry(models.Model):
    idtblreturnEntry = models.AutoField(primary_key=True)
    bill_date = models.CharField(null=True, max_length=20)
    bill_no = models.CharField(null=True, max_length=20)
    customer_name = models.CharField(max_length=200, null=True)
    customer_pan = models.CharField(max_length=200, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    NoTaxSales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ZeroTaxSales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    miti = models.CharField(null=True, max_length=20)
    ServicedItem = models.CharField(max_length=20, default="Goods")
    quantity = models.PositiveIntegerField(default=1)
    reason = models.TextField(null=True, blank=True)
    exemptedSales = models.CharField(default="0", max_length=20)
    export = models.CharField(default="0", max_length=20)
    exportCountry = models.CharField(default="0", max_length=20)
    exportNumber = models.CharField(default="0", max_length=20)
    exportDate = models.CharField(default="0", max_length=20)
    unit = models.CharField(default="-", max_length=20)
    excise_duty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fiscal_year = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "tblreturnentry"

    def __str__(self):
        return f"{self.idtblreturnEntry}- {self.bill_date} - {self.bill_no}"


class PaymentType(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Payment Type Title")
    description = models.TextField(null=True, verbose_name="Payment Type Description")
    icon = models.ImageField(upload_to="payment-type/icons/", null=True, blank=True)
    slug = models.SlugField(unique=True, verbose_name="Payment Type Slug")

    def __str__(self):
        return self.title 


class BillItem(BaseModel):
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(
        max_length=255, verbose_name="Product Title", null=True
    )
    product_quantity = models.PositiveBigIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_title = models.CharField(max_length=50, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_taxable = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.product_title}"




''' Signal for Decresing Product Stock after Sold '''

def update_stock(sender, instance, **kwargs):
    # stock = ProductStock.objects.get(product=instance.product)
    # try:
    #     stock.stock_quantity = stock.stock_quantity - int(instance.product_quantity)
    #     stock.save()
    # except Exception as e:
    #     print(e)
    product_sold(instance=instance)
    

post_save.connect(update_stock, sender=BillItem)

# def update_stock(sender, instance, **kwargs):
#     bill = instance.bill_set.first()
#     quantity = instance.product_quantity
#     if bill:
#         branchstock_entries = BranchStock.objects.filter(branch=bill.branch, product=instance.product, is_deleted=False).order_by('quantity')
        
#         for branchstock in branchstock_entries:
#                 if quantity > 0:
#                     available_quantity = branchstock.quantity
#                     if quantity >= available_quantity:
#                         # Reduce the available quantity to 0 and update the branchstock entry
#                         branchstock.quantity = 0
#                         branchstock.save()
#                         quantity -= available_quantity
#                     else:
#                         # Reduce the available quantity by the bill item quantity and update the branchstock entry
#                         branchstock.quantity -= quantity
#                         branchstock.save()
#                         quantity = 0
#         print("Quantity updated")
#     product_sold(instance=instance)

# post_save.connect(update_stock, sender=BillItem)




""" **************************************** """


class BillIndex(BaseModel):
    terminal = models.CharField(max_length=255)
    bill_index = models.PositiveBigIntegerField(default=1)
    branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.terminal} {self.bill_index} {self.branch.branch_code}"

class Bill(BaseModel):
    class BillType(models.TextChoices):
        SALE = 'Sale', 'Sale'
        RENTAL = 'Rental', 'Rental'
        OTHERS = 'Others', 'Others'
    bill_type = models.CharField(max_length=20, choices=BillType.choices, default=BillType.SALE)  # add this line
    fiscal_year = models.CharField(max_length=20)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    agent_name = models.CharField(max_length=255, null=True)
    terminal = models.CharField(max_length=10, default="1")
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_address = models.CharField(max_length=255, null=True, blank=True)
    customer_tax_number = models.CharField(max_length=255, null=True, blank=True)
    customer = models.ForeignKey("user.Customer", on_delete=models.SET_NULL, null=True)
    transaction_date_time = models.DateTimeField(auto_now_add=True)
    transaction_date = models.DateField(auto_now_add=True)

    transaction_miti = models.CharField(max_length=255, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    excise_duty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    invoice_number = models.CharField(max_length=255, null=True, blank=True)
    amount_in_words = models.TextField(null=True, blank=True)
    payment_mode = models.CharField(
        max_length=255, default="Cash", blank=True, null=True
    )

    bill_items = models.ManyToManyField(BillItem, blank=True)
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.SET_NULL, null=True
    )
    branch = models.ForeignKey(
        "organization.Branch", on_delete=models.SET_NULL, null=True
    )
    print_count = models.PositiveIntegerField(default=1)
    # is_taxable = models.BooleanField(default=True)
    bill_count_number = models.PositiveIntegerField(blank=True, null=True, db_index=True)   
    is_end_day = models.BooleanField(default=False)
    narration = models.TextField(null=True, blank=True)
    previous_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    
    # --- IRD sync tracking ---
    ird_synced = models.BooleanField(default=False, db_index=True)
    ird_sync_error = models.TextField(null=True, blank=True)
    ird_last_attempt_at = models.DateTimeField(null=True, blank=True)
    ird_retry_count = models.PositiveIntegerField(default=0)
    ird_response = models.JSONField(null=True, blank=True) 

    class Meta:
        unique_together = 'invoice_number', 'fiscal_year', 'branch'

    def __str__(self):
        return f"{self.customer_name}-{self.transaction_date}- {self.grand_total}"

    def recalculate_rental_totals(self):
        """Call this after attaching/updating BillRent rows for this bill."""
        items = self.rental_details.all()
        self.sub_total = sum(i.subtotal for i in items)
        self.taxable_amount = sum(i.taxable_amount for i in items)
        self.tax_amount = sum(i.vat_amount for i in items)
        self.grand_total = sum(i.total for i in items)
        self.save(update_fields=['sub_total', 'taxable_amount', 'tax_amount', 'grand_total'])

    # def recalculate_other_totals(self):
    #     """
    #     Call this after attaching/updating BillOtherItem rows for this bill.
    #     Sums item totals only -- discount_amount is applied separately at
    #     the bill level afterward (see OtherBillCreateAPIView.post), since
    #     discount here is flat-per-bill, not per item.
    #     """
    #     items = self.other_details.filter(is_deleted=False)
    #     self.sub_total = sum(i.subtotal for i in items)
    #     self.taxable_amount = sum(i.subtotal for i in items)
    #     self.tax_amount = sum(i.vat_amount for i in items)
    #     self.grand_total = sum(i.total for i in items)
    #     self.save(update_fields=['sub_total', 'taxable_amount', 'tax_amount', 'grand_total'])

    def recalculate_other_totals(self):
        """
        Call this after attaching/updating BillOtherItem rows for this bill.
        Sums item totals only -- discount_amount is applied separately at
        the bill level afterward (see OtherBillCreateAPIView.post), since
        discount here is flat-per-bill, not per item.
        """
        items = self.other_details.filter(is_deleted=False)
        self.sub_total = sum(i.subtotal for i in items)
        # Only taxable items' subtotal counts toward the taxable base --
        # non-taxable items still contribute to sub_total/grand_total but
        # should never inflate taxable_amount.
        self.taxable_amount = sum(i.subtotal for i in items if i.is_taxable)
        self.tax_amount = sum(i.vat_amount for i in items)
        self.grand_total = sum(i.total for i in items)
        self.save(update_fields=['sub_total', 'taxable_amount', 'tax_amount', 'grand_total'])
 
 

    
from django.db import transaction

@receiver(post_save, sender=Bill)
def create_invoice_number(sender, instance, created, **kwargs):
    from datetime import datetime
    import nepali_datetime
    current_fiscal_year = Organization.objects.last().current_fiscal_year

    if created and not instance.payment_mode.lower() == "complimentary":
        branch_code = instance.branch.branch_code
        branch = instance.branch
        current_terminal = instance.terminal

        instance.fiscal_year = current_fiscal_year
        instance.transaction_date = datetime.today()
        instance.transaction_miti = nepali_datetime.date.today()

        with transaction.atomic():
            terminal_obj = (
                BillIndex.objects.select_for_update()
                .filter(terminal=current_terminal, branch=branch)
                .last()
            )

            if terminal_obj:
                bill_index = terminal_obj.bill_index + 1
                terminal_obj.bill_index = bill_index
                terminal_obj.save()
                branch_code = terminal_obj.branch.branch_code
                current_terminal = terminal_obj.terminal
            else:
                bill_index = 1
                terminal_obj = BillIndex.objects.create(
                    terminal=current_terminal, bill_index=bill_index, branch=branch
                )
                branch_code = branch.branch_code

            invoice_no = f"{branch_code}-{current_terminal}-{bill_index}"

            duplicate_exists = Bill.objects.filter(
                invoice_number=invoice_no,
                fiscal_year=current_fiscal_year,
                branch=instance.branch,
                is_deleted=False
            ).exists()

            if duplicate_exists:
                print(f"Skipping bill creation: duplicate invoice {invoice_no}")
                return
            else:
                instance.invoice_number = invoice_no

        # --- RENTAL bills stop here: totals aren't final yet.
        # The view calls finalize_rental_bill_accounting() itself, after
        # recalculate_rental_totals() sets real numbers.
        if instance.bill_type == Bill.BillType.RENTAL:
            instance.save()
            return

        if instance.bill_type == Bill.BillType.OTHERS:
            instance.save()
            return

        # --- everything below is unchanged, for non-rental bills only ---
        a = TblTaxEntry(
            fiscal_year=current_fiscal_year,
            bill_no=invoice_no,
            customer_name=instance.customer_name,
            customer_pan=instance.customer_tax_number,
            bill_date=instance.transaction_date.strftime('%Y-%m-%d'),
            amount=instance.grand_total,
            taxable_amount=instance.taxable_amount,
            tax_amount=instance.tax_amount,
            is_printed="Yes",
            printed_time=str(datetime.now().time().strftime("%I:%M %p")),
            entered_by=instance.agent_name,
            printed_by=instance.agent_name,
            is_realtime="Yes",
            sync_with_ird="Yes",
            payment_method=instance.payment_mode,
            vat_refund_amount=0.0,
            transaction_id="-",
        )

        b = TblSalesEntry(
            bill_date=instance.transaction_date.strftime('%Y-%m-%d'),
            customer_name=instance.customer_name,
            customer_pan=instance.customer_tax_number,
            amount=instance.grand_total,
            NoTaxSales=0.0,
            ZeroTaxSales=0.0,
            taxable_amount=instance.taxable_amount,
            tax_amount=instance.tax_amount,
            miti=str(instance.transaction_miti),
            ServicedItem="Goods",
            quantity=1.0,
            bill_no=invoice_no,
            excise_duty_amount=instance.excise_duty_amount
        )

        try:
            create_journal_for_bill(instance)
        except Exception as e:
            pass

        if instance.tax_amount == 0:
            a.exemptedSales = instance.sub_total
            b.exemptedSales = instance.sub_total

        b.save()
        a.save()
        instance.save()

    if created and instance.payment_mode.lower().strip() == "complimentary":
        instance.tax_amount = 0
        instance.taxable_amount = 0
        instance.discount_amount = 0
        instance.save()
        try:
            create_journal_for_complimentary(instance)
        except Exception as e:
            pass


class BillPayment(BaseModel):
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT)
    payment_mode = models.CharField(max_length=100)
    rrn = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return self.payment_mode
    
class ConflictBillNumber(BaseModel):
    invoice_number = models.CharField(max_length=50)

    def __str__(self):
        return self.invoice_number
        
class MobilePaymentType(BaseModel):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    icon = models.ImageField(upload_to="mobile-payment-type/icons/", null=True, blank=True)
    qr = models.ImageField(upload_to="mobile-payment-type/qr/", null=True, blank=True)

    def __str__(self):
        return self.name 
    
    def get_qr(self):
        if self.qr :
            return self.qr.url
        else:
            return None
        
    def get_icon(self):
        if self.icon :
            return self.icon.url
        else:
            return None
            
class MobilePaymentSummary(BaseModel):
     type = models.ForeignKey(MobilePaymentType, models.CASCADE)
     value = models.DecimalField(max_digits=9, decimal_places=2, default=0)
     bill = models.ForeignKey(Bill, models.CASCADE, null=True, blank=True)
     branch = models.ForeignKey(Branch, models.CASCADE, null=True, blank=True)
     terminal = models.CharField(max_length=255, null=True, blank=True)
     sent_in_mail = models.BooleanField(default=False)


class CreditNote(BaseModel):
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    ref_billno = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True)
    customer_pan = models.CharField(max_length=200, null=True)
    # product = models.ForeignKey("product.Product", models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey("user.Customer", on_delete=models.SET_NULL, null=True)  
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.SET_NULL, null=True
    )
    branch = models.ForeignKey(
        "organization.Branch", on_delete=models.SET_NULL, null=True
    )

class CreditNoteDetails(BaseModel):
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product = models.ForeignKey("product.Product", models.CASCADE, null=True, blank=True)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creditnote = models.ForeignKey(CreditNote, models.CASCADE, null=True, blank=True)

class IrdCredentials(BaseModel):
    outlet_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    seller_pan = models.CharField(max_length=255)

class EstimatedBill(BaseModel):
    customer = models.ForeignKey(
        "user.Customer",  # adjust import path as needed
        on_delete=models.PROTECT,
        related_name="estimated_bills",
    )
    payment_mode = models.CharField(max_length=255, default="Cash")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Bill-level totals, supplied by frontend (same pattern as OtherBill)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    narration = models.CharField(max_length=255, default="Cash")

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"EstimatedBill #{self.pk} - {self.customer}"


class EstimatedBillItem(BaseModel):
    bill = models.ForeignKey(
        EstimatedBill, on_delete=models.CASCADE, related_name="items"
    )
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    is_taxable = models.BooleanField(default=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"