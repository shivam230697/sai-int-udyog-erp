from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Party(TimeStampedModel):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    BOTH = "both"
    PARTY_TYPES = [(CUSTOMER, "Customer"), (SUPPLIER, "Supplier"), (BOTH, "Customer and Supplier")]

    name = models.CharField(max_length=180)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPES)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    state = models.CharField(max_length=100, default="Madhya Pradesh")
    state_code = models.CharField(max_length=2, blank=True)
    gstin = models.CharField(max_length=15, blank=True)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"),
                                          help_text="Positive means party owes the business; negative means business owes the party.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RawMaterial(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    unit = models.CharField(max_length=20, default="tonne", help_text="e.g. tonne, kg, tractor-load")
    reorder_level = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Purchase(TimeStampedModel):
    date = models.DateField(default=timezone.localdate)
    voucher_no = models.CharField(max_length=40, unique=True)
    supplier = models.ForeignKey(Party, on_delete=models.PROTECT, related_name="purchases")
    material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT, related_name="purchases")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0.001"))])
    unit_rate = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    freight = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"), help_text="Confirm applicable GST rate with your accountant.")
    notes = models.TextField(blank=True)

    @property
    def taxable_value(self):
        return self.quantity * self.unit_rate + self.freight

    @property
    def tax_amount(self):
        return self.taxable_value * self.tax_rate / Decimal("100")

    @property
    def total_amount(self):
        return self.taxable_value + self.tax_amount

    def __str__(self):
        return self.voucher_no


class KilnBatch(TimeStampedModel):
    STATUS_CHOICES = [
        ("forming", "Forming"), ("drying", "Drying"), ("loaded", "Loaded in kiln"),
        ("firing", "Firing"), ("cooling", "Cooling"), ("completed", "Completed"),
    ]
    batch_no = models.CharField(max_length=40, unique=True)
    start_date = models.DateField(default=timezone.localdate)
    kiln_name = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="forming")
    clay_used = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"), help_text="Quantity in the selected clay unit.")
    fuel_used = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"), help_text="Quantity in the selected fuel unit.")
    green_bricks = models.PositiveIntegerField(default=0)
    loaded_bricks = models.PositiveIntegerField(default=0)
    good_bricks = models.PositiveIntegerField(default=0)
    damaged_bricks = models.PositiveIntegerField(default=0)
    rejected_bricks = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    @property
    def accounted_bricks(self):
        return self.good_bricks + self.damaged_bricks + self.rejected_bricks

    @property
    def yield_percent(self):
        if not self.loaded_bricks:
            return Decimal("0")
        return (Decimal(self.good_bricks) / Decimal(self.loaded_bricks)) * Decimal("100")

    def __str__(self):
        return self.batch_no


class StockMovement(TimeStampedModel):
    MOVEMENT_TYPES = [
        ("opening", "Opening balance"), ("production", "Production receipt"),
        ("sale", "Sale dispatch"), ("return", "Customer return"),
        ("damage", "Damage/write-off"), ("adjustment", "Stock adjustment"),
    ]
    date = models.DateField(default=timezone.localdate)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity_change = models.IntegerField(help_text="Positive adds bricks to stock; negative removes bricks.")
    reference = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.date} · {self.movement_type} · {self.quantity_change}"


class Sale(TimeStampedModel):
    STATUS_CHOICES = [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")]
    date = models.DateField(default=timezone.localdate)
    invoice_no = models.CharField(max_length=40, unique=True)
    customer = models.ForeignKey(Party, on_delete=models.PROTECT, related_name="sales")
    brick_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    rate_per_1000 = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    freight = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"), help_text="Confirm applicable GST rate with your accountant.")
    vehicle_no = models.CharField(max_length=20, blank=True)
    driver_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True)

    @property
    def taxable_value(self):
        return (Decimal(self.brick_quantity) / Decimal("1000")) * self.rate_per_1000 + self.freight

    @property
    def tax_amount(self):
        return self.taxable_value * self.tax_rate / Decimal("100")

    @property
    def total_amount(self):
        return self.taxable_value + self.tax_amount

    def __str__(self):
        return self.invoice_no


class Payment(TimeStampedModel):
    IN = "in"
    OUT = "out"
    DIRECTIONS = [(IN, "Received"), (OUT, "Paid")]
    METHODS = [("cash", "Cash"), ("bank", "Bank transfer"), ("upi", "UPI"), ("cheque", "Cheque"), ("other", "Other")]

    date = models.DateField(default=timezone.localdate)
    voucher_no = models.CharField(max_length=40, unique=True)
    direction = models.CharField(max_length=3, choices=DIRECTIONS)
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    method = models.CharField(max_length=10, choices=METHODS, default="cash")
    reference_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.voucher_no


class Expense(TimeStampedModel):
    date = models.DateField(default=timezone.localdate)
    voucher_no = models.CharField(max_length=40, unique=True)
    category = models.CharField(max_length=100, help_text="e.g. labour, coal/fuel, electricity, repairs, loading")
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    paid_from = models.CharField(max_length=10, choices=[("cash", "Cash"), ("bank", "Bank")], default="cash")
    supplier = models.ForeignKey(Party, on_delete=models.PROTECT, null=True, blank=True, related_name="expenses")
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.voucher_no


class Account(TimeStampedModel):
    ACCOUNT_TYPES = [
        ("asset", "Asset"), ("liability", "Liability"), ("equity", "Equity"),
        ("income", "Income"), ("expense", "Expense"),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    account_type = models.CharField(max_length=12, choices=ACCOUNT_TYPES)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class JournalEntry(TimeStampedModel):
    date = models.DateField(default=timezone.localdate)
    entry_no = models.CharField(max_length=40, unique=True)
    narration = models.CharField(max_length=250)
    source_type = models.CharField(max_length=30, blank=True)
    source_id = models.PositiveBigIntegerField(null=True, blank=True)
    posted = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.entry_no


class JournalLine(TimeStampedModel):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="journal_lines")
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    party = models.ForeignKey(Party, on_delete=models.PROTECT, null=True, blank=True, related_name="journal_lines")
    memo = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.entry.entry_no} · {self.account.name}"
