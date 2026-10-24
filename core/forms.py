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
