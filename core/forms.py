from django import forms
from .models import KilnBatch

class KilnBatchForm(forms.ModelForm):
    class Meta:
        model = KilnBatch
        fields = [
            "batch_no", "start_date", "kiln_name", "status", "clay_used", "fuel_used",
            "green_bricks", "loaded_bricks", "good_bricks", "damaged_bricks",
            "rejected_bricks", "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
        self.fields["batch_no"].widget.attrs["placeholder"] = "e.g. KILN-2026-001"
        self.fields["kiln_name"].widget.attrs["placeholder"] = "e.g. Main kiln"


from .models import Party


class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = [
            "name", "party_type", "phone", "email", "address",
            "state", "state_code", "gstin", "opening_balance", "is_active",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "opening_balance": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
        self.fields["name"].widget.attrs["placeholder"] = "Customer or supplier name"
        self.fields["phone"].widget.attrs["placeholder"] = "Mobile number"
        self.fields["gstin"].widget.attrs["maxlength"] = "15"


from .models import RawMaterial, Purchase, Sale, Payment, Expense, StockMovement, Account


class BaseStyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-select" if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else "form-control")


class RawMaterialForm(BaseStyledModelForm):
    class Meta:
        model = RawMaterial
        fields = ["name", "unit", "reorder_level", "is_active"]


class PurchaseForm(BaseStyledModelForm):
    class Meta:
        model = Purchase
        fields = ["date", "voucher_no", "supplier", "material", "quantity", "unit_rate", "freight", "tax_rate", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Party.objects.filter(party_type__in=["supplier", "both"], is_active=True)
        self.fields["material"].queryset = RawMaterial.objects.filter(is_active=True)


class SaleForm(BaseStyledModelForm):
    class Meta:
        model = Sale
        fields = ["date", "invoice_no", "customer", "brick_quantity", "rate_per_1000", "freight", "tax_rate", "vehicle_no", "driver_name", "status", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Party.objects.filter(party_type__in=["customer", "both"], is_active=True)


class PaymentForm(BaseStyledModelForm):
    class Meta:
        model = Payment
        fields = ["date", "voucher_no", "direction", "party", "amount", "method", "reference_no", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["party"].queryset = Party.objects.filter(is_active=True)


class ExpenseForm(BaseStyledModelForm):
    class Meta:
        model = Expense
        fields = ["date", "voucher_no", "category", "description", "amount", "tax_amount", "paid_from", "supplier", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Party.objects.filter(party_type__in=["supplier", "both"], is_active=True)


class StockMovementForm(BaseStyledModelForm):
    class Meta:
        model = StockMovement
        fields = ["date", "movement_type", "quantity_change", "reference", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3})}


class AccountForm(BaseStyledModelForm):
    class Meta:
        model = Account
        fields = ["code", "name", "account_type", "is_active"]
