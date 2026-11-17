from django.db import models

# Create your models here.

from root.utils import BaseModel


# class SpaceSlot(BaseModel):
#     class StatusChoices(models.TextChoices):
#         VACANT = 'Vacant', 'Vacant'
#         OCCUPIED = 'Occupied', 'Occupied'
#         RESERVED = 'Reserved', 'Reserved'  # Optional additional status
#         MAINTENANCE = 'Maintenance', 'Maintenance'  # Optional additional status

#     floor = models.CharField(max_length=50, help_text="Floor number or name (e.g., 'Ground', '1st', 'Basement')")
#     spaceno = models.CharField(max_length=50, unique=True, help_text="Unique space number identifier")
#     status = models.CharField(
#         max_length=20,
#         choices=StatusChoices.choices,
#         default=StatusChoices.VACANT,
#         help_text="Current availability status of the space"
#     )

#     class Meta:
#         ordering = ['floor', 'spaceno']
#         unique_together = [['floor', 'spaceno']]  # Prevent duplicate space numbers on same floor
#         indexes = [
#             models.Index(fields=['floor', 'status']),
#             models.Index(fields=['spaceno']),
#         ]

#     def __str__(self):
#         return f"{self.spaceno} - {self.floor} ({self.status})"

#     def is_available(self):
#         """Check if the space is currently available for rent"""
#         return self.status == self.StatusChoices.VACANT

#     def occupy(self):
#         """Mark the space as occupied"""
#         self.status = self.StatusChoices.OCCUPIED
#         self.save()

#     def vacate(self):
#         """Mark the space as vacant"""
#         self.status = self.StatusChoices.VACANT
#         self.save()


class SpaceSlot(BaseModel):
    class StatusChoices(models.TextChoices):
        VACANT = 'Vacant', 'Vacant'
        OCCUPIED = 'Occupied', 'Occupied'
        RESERVED = 'Reserved', 'Reserved'
        MAINTENANCE = 'Maintenance', 'Maintenance'

    floor = models.CharField(max_length=50, help_text="Floor number or name")
    spaceno = models.CharField(max_length=50, help_text="Unique space number identifier", null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.VACANT)

    # Physical meter seed readings — belong to the space, not the tenant
    initial_nea_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    initial_diesel_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    reading_for = models.CharField(
        max_length=20, null=True, blank=True,
        help_text="Month/year that initial_nea_reading and initial_diesel_reading were recorded for, e.g. 'August 2026'"
    )
    class Meta:
        ordering = ['floor', 'spaceno']
        # unique_together = [['floor', 'spaceno']]
        indexes = [
            models.Index(fields=['floor', 'status']),
            models.Index(fields=['spaceno']),
        ]

    def __str__(self):
        return f"{self.spaceno} - {self.floor} ({self.status})"

    def is_available(self):
        return self.status == self.StatusChoices.VACANT

    def occupy(self):
        self.status = self.StatusChoices.OCCUPIED
        self.save()

    def vacate(self):
        self.status = self.StatusChoices.VACANT
        self.save()

from django.db import models
from django.core.validators import RegexValidator


class Business(BaseModel):

    company_name = models.CharField(max_length=255)
    pan_number = models.CharField(
        max_length=10, null=True, blank=True
    )
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=40, null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    customer = models.OneToOneField(
        "user.Customer",  # adjust app label to wherever Customer actually lives
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="business",
    )
    def __str__(self):
        return self.company_name



# models.py
from django.db import models
from root.utils import BaseModel


class Contract(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        EXPIRED = 'Expired', 'Expired'
        TERMINATED = 'Terminated', 'Terminated'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='contracts')
    slot = models.ForeignKey(SpaceSlot, on_delete=models.CASCADE, related_name='contracts')
    contract_signed_date = models.DateField()
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)

    # NEW: negotiated rates for this tenancy
    nea_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Rate per unit for NEA electricity")
    diesel_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Rate per unit for diesel generator electricity")
    cam_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Fixed monthly common area maintenance charge")

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        ordering = ['-contract_start_date']
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['slot', 'status']),
        ]

    def __str__(self):
        return f"{self.business.company_name} - {self.slot.spaceno} ({self.status})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.StatusChoices.ACTIVE:
            self.slot.occupy()


from user.models import User

from django.core.exceptions import ValidationError


class ElectricityVatConfig(BaseModel):
    """VAT rule applied to combined NEA + diesel units consumed in a month."""
    vat_threshold_units = models.DecimalField(
        max_digits=10, decimal_places=2, default=50,
        help_text="VAT applies if total units consumed (NEA + diesel) exceed this"
    )
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=13)
    effective_from = models.DateField(help_text="This rate applies from this date onward")

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"VAT {self.vat_percent}% over {self.vat_threshold_units} units (from {self.effective_from})"


class BillRent(BaseModel):
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    slot = models.ForeignKey(SpaceSlot, on_delete=models.SET_NULL, null=True, related_name='bill_rent_items')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, related_name='bill_rent_items')
    bill_month = models.DateField(help_text="1st of billing month, e.g. 2026-08-01")
    bill_nepali_month = models.CharField(
        max_length=10,
        help_text="BS billing month, format YYYY-MM-01, e.g. 2083-04-01", null=True, blank=True
    )

    # NEA meter
    nea_old_unit = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    nea_current_unit = models.DecimalField(max_digits=10, decimal_places=2)
    nea_unit_diff = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    nea_rate = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    nea_subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Diesel generator meter
    diesel_old_unit = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    diesel_current_unit = models.DecimalField(max_digits=10, decimal_places=2)
    diesel_unit_diff = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    diesel_rate = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    diesel_subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Flat charges — entered directly per bill
    cam_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ac_electricity_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Rent — snapshotted from Contract, exempt from VAT
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # --- Totals, now separated ---
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, editable=False,
        help_text="Everything before VAT: NEA + Diesel + CAM + AC electricity + Rent"
    )
    taxable_amount = models.DecimalField(
        max_digits=12, decimal_places=2, editable=False,
        help_text="Portion of subtotal that VAT is calculated on (everything except rent)"
    )
    is_taxable = models.BooleanField(default=False, editable=False)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False, help_text="subtotal + vat_amount")

    bill = models.ForeignKey(
        "bill.Bill", on_delete=models.CASCADE, null=True, blank=True, related_name='rental_details'
    )

    class Meta:
        ordering = ['-bill_month']
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['slot', 'bill_month'],
        #         condition=models.Q(is_deleted=False),
        #         name='unique_active_slot_bill_month',
        #     )
        # ]

    def __str__(self):
        return f"{self.slot.spaceno if self.slot else ''} - {self.bill_month}"

    # def _get_old_units(self):
    #     last = (
    #         BillRent.objects
    #         .filter(slot=self.slot)
    #         .exclude(pk=self.pk)
    #         .order_by('-bill_month')
    #         .first()
    #     )
    #     if last:
    #         return last.nea_current_unit, last.diesel_current_unit
    #     return self.slot.initial_nea_reading, self.slot.initial_diesel_reading

    def save(self, *args, **kwargs):
        duplicate_exists = (
            BillRent.objects
            .filter(slot=self.slot, bill_month=self.bill_month, is_deleted=False)
            .exclude(pk=self.pk)
            .exists()
        )
        if duplicate_exists:
            raise ValidationError("A bill for this slot and month already exists.")

        later_exists = (
            BillRent.objects
            .filter(slot=self.slot, bill_month__gt=self.bill_month, is_deleted=False)
            .exclude(pk=self.pk)
            .exists()
        )
        if later_exists:
            raise ValidationError("Cannot insert a reading for this month — a later bill already exists for this slot.")
        if not self.contract:
            raise ValidationError("A contract is required to determine rates and rent.")

        # nea_old_unit / diesel_old_unit now come in directly from the request —
        # no _get_old_units() lookup, no SpaceSlot fallback.
        if self.nea_current_unit < self.nea_old_unit:
            raise ValidationError(f"{self.slot} NEA current unit cannot be less than old unit.")
        if self.diesel_current_unit < self.diesel_old_unit:
            raise ValidationError("Diesel current unit cannot be less than old unit.")

        self.nea_unit_diff = self.nea_current_unit - self.nea_old_unit
        self.diesel_unit_diff = self.diesel_current_unit - self.diesel_old_unit

        self.nea_rate = self.contract.nea_rate
        self.diesel_rate = self.contract.diesel_rate
        self.nea_subtotal = self.nea_unit_diff * self.nea_rate
        self.diesel_subtotal = self.diesel_unit_diff * self.diesel_rate

        self.cam_amount = self.contract.cam_amount
        self.rent_amount = self.contract.monthly_rent

        self.taxable_amount = (
            self.nea_subtotal + self.diesel_subtotal + self.cam_amount + self.ac_electricity_amount
        )
        self.subtotal = self.taxable_amount + self.rent_amount

        from decimal import Decimal
        self.is_taxable = True
        self.vat_amount = self.taxable_amount * Decimal("0.13")
        self.total = self.subtotal + self.vat_amount

        super().save(*args, **kwargs)
        # No slot sync needed — the slot's initial_nea_reading/initial_diesel_reading
        # only ever mattered as a first-bill seed; the frontend now sources "old unit"
        # from wherever it already gets last-bill data (e.g. RentalBillDetailAPIView /
        # the list GET), so there's nothing left for the slot fields to keep in sync with.

    # def _get_old_units(self):
    #     last = (
    #         BillRent.objects
    #         .filter(slot=self.slot, is_deleted=False)
    #         .exclude(pk=self.pk)
    #         .order_by('-bill_month')
    #         .first()
    #     )
    #     if last:
    #         return last.nea_current_unit, last.diesel_current_unit
    #     return self.slot.initial_nea_reading, self.slot.initial_diesel_reading


    # def save(self, *args, **kwargs):
    #     # duplicate_exists = (
    #     #     BillRent.objects
    #     #     .filter(slot=self.slot, bill_month=self.bill_month)
    #     #     .exclude(pk=self.pk)
    #     #     .exists()
    #     # )
    #     # if duplicate_exists:
    #     #     raise ValidationError("A bill for this slot and month already exists.")

    #     # later_exists = (
    #     #     BillRent.objects
    #     #     .filter(slot=self.slot, bill_month__gt=self.bill_month)
    #     #     .exclude(pk=self.pk)
    #     #     .exists()
    #     # )
    #     # if later_exists:
    #     #     raise ValidationError("Cannot insert a reading for this month — a later bill already exists for this slot.")

    #     duplicate_exists = (
    #         BillRent.objects
    #         .filter(slot=self.slot, bill_month=self.bill_month, is_deleted=False)
    #         .exclude(pk=self.pk)
    #         .exists()
    #     )
    #     if duplicate_exists:
    #         raise ValidationError("A bill for this slot and month already exists.")

    #     later_exists = (
    #         BillRent.objects
    #         .filter(slot=self.slot, bill_month__gt=self.bill_month, is_deleted=False)
    #         .exclude(pk=self.pk)
    #         .exists()
    #     )
    #     if later_exists:
    #         raise ValidationError("Cannot insert a reading for this month — a later bill already exists for this slot.")
    #     if not self.contract:
    #         raise ValidationError("A contract is required to determine rates and rent.")

    #     self.nea_old_unit, self.diesel_old_unit = self._get_old_units()

    #     if self.nea_current_unit < self.nea_old_unit:
    #         raise ValidationError(f" slot {self.slot.id} contract {self.contract.id} NEA current unit cannot be less than old unit.")
    #     if self.diesel_current_unit < self.diesel_old_unit:
    #         raise ValidationError(f" slot {self.slot.id} contract {self.contract.id} Diesel current unit cannot be less than old unit.")

    #     self.nea_unit_diff = self.nea_current_unit - self.nea_old_unit
    #     self.diesel_unit_diff = self.diesel_current_unit - self.diesel_old_unit

    #     self.nea_rate = self.contract.nea_rate
    #     self.diesel_rate = self.contract.diesel_rate
    #     self.nea_subtotal = self.nea_unit_diff * self.nea_rate
    #     self.diesel_subtotal = self.diesel_unit_diff * self.diesel_rate

    #     # CAM now pulled from contract, same as nea_rate/diesel_rate — no longer user-entered
    #     self.cam_amount = self.contract.cam_amount

    #     self.rent_amount = self.contract.monthly_rent

    #     self.taxable_amount = (
    #         self.nea_subtotal + self.diesel_subtotal + self.cam_amount + self.ac_electricity_amount
    #     )
    #     self.subtotal = self.taxable_amount + self.rent_amount

    #     from decimal import Decimal
    #     self.is_taxable = True
    #     self.vat_amount = self.taxable_amount * Decimal("0.13")

    #     self.total = self.subtotal + self.vat_amount

    #     super().save(*args, **kwargs)


# import decimal
# from django.db import models


# class BillOtherItem(BaseModel):
#     """
#     Line items for Bill.BillType.OTHERS bills (e.g. Advertisement, Service
#     Charge, or any ad-hoc billable item that isn't a product Sale or Rental).
#     Sum of active rows' subtotal/vat_amount/total must equal the parent
#     Bill's taxable_amount/tax_amount/grand_total -- see
#     Bill.recalculate_other_totals().
#     """

#     TAX_RATE = decimal.Decimal('0.13')  # adjust to your actual VAT rate

#     bill = models.ForeignKey(
#         "bill.Bill", on_delete=models.CASCADE, related_name='other_details'
#     )
#     item_name = models.CharField(max_length=255)
#     quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
#     rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     is_taxable = models.BooleanField(default=True)

#     # ---- Discount: flat amount, set directly by the caller ----
#     discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     is_deleted = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = "Bill Other Item"
#         verbose_name_plural = "Bill Other Items"

#     def __str__(self):
#         return f"{self.item_name} - {self.bill.invoice_number}"

#     def save(self, *args, **kwargs):
#         # Auto-derive subtotal/vat_amount/total from quantity, rate,
#         # discount_amount and is_taxable -- discount_amount itself is now
#         # a direct input, not computed here.
#         raw_subtotal = (self.quantity or 0) * (self.rate or 0)
#         discount = self.discount_amount or decimal.Decimal('0.00')

#         # subtotal is the discounted, pre-tax amount -- this is what VAT and
#         # the bill's taxable_amount are calculated from.
#         self.subtotal = raw_subtotal - discount

#         if self.is_taxable:
#             self.vat_amount = (self.subtotal * self.TAX_RATE).quantize(decimal.Decimal('0.01'))
#         else:
#             self.vat_amount = decimal.Decimal('0.00')

#         self.total = self.subtotal + self.vat_amount
#         super().save(*args, **kwargs)

import decimal
from django.db import models


class BillOtherItem(BaseModel):
    """
    Line items for Bill.BillType.OTHERS bills (e.g. Advertisement, Service
    Charge, or any ad-hoc billable item that isn't a product Sale or Rental).
    Sum of active rows' subtotal/vat_amount/total feeds into the parent
    Bill's taxable_amount/tax_amount/grand_total -- see
    Bill.recalculate_other_totals(). Discount is applied at the BILL level,
    not per item -- see Bill.discount_amount and OtherBillCreateAPIView.
    """

    TAX_RATE = decimal.Decimal('0.13')  # adjust to your actual VAT rate

    bill = models.ForeignKey(
        "bill.Bill", on_delete=models.CASCADE, related_name='other_details'
    )
    
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_taxable = models.BooleanField(default=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Bill Other Item"
        verbose_name_plural = "Bill Other Items"

    def __str__(self):
        return f"{self.item_name} - {self.bill.invoice_number}"

    # def save(self, *args, **kwargs):
    #     # Auto-derive subtotal/vat_amount/total from quantity, rate, is_taxable
    #     # so callers only ever need to set item_name/quantity/rate/is_taxable.
    #     self.subtotal = (self.quantity or 0) * (self.rate or 0)

    #     if self.is_taxable:
    #         self.vat_amount = (self.subtotal * self.TAX_RATE).quantize(decimal.Decimal('0.01'))
    #     else:
    #         self.vat_amount = decimal.Decimal('0.00')

    #     self.total = self.subtotal + self.vat_amount
    #     super().save(*args, **kwargs)