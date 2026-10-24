from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import (KilnBatchForm, PartyForm, RawMaterialForm, PurchaseForm, SaleForm, PaymentForm, ExpenseForm, StockMovementForm, AccountForm)
from .models import KilnBatch, Sale, StockMovement, Expense, Purchase, Party, RawMaterial, Payment, Account


@login_required
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    production_today = KilnBatch.objects.filter(start_date=today).aggregate(total=Sum("good_bricks"))["total"] or 0
    production_month = KilnBatch.objects.filter(start_date__gte=month_start, start_date__lte=today).aggregate(total=Sum("good_bricks"))["total"] or 0
    sales_month = Sale.objects.filter(date__gte=month_start, date__lte=today, status="posted")
    sales_value = sum((sale.total_amount for sale in sales_month), start=0)
    stock_balance = StockMovement.objects.aggregate(total=Sum("quantity_change"))["total"] or 0
    expenses_month = Expense.objects.filter(date__gte=month_start, date__lte=today).aggregate(total=Sum("amount"))["total"] or 0
    recent_batches = KilnBatch.objects.order_by("-start_date", "-id")[:5]
    context = {
        "today": today,
        "production_today": production_today,
        "production_month": production_month,
        "sales_count_month": sales_month.count(),
        "sales_value_month": sales_value,
        "stock_balance": stock_balance,
        "expenses_month": expenses_month,
        "recent_batches": recent_batches,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def production_list(request):
    batches = KilnBatch.objects.order_by("-start_date", "-id")
    return render(request, "core/production_list.html", {"batches": batches})


@login_required
def production_create(request):
    if request.method == "POST":
        form = KilnBatchForm(request.POST)
        if form.is_valid():
            batch = form.save()
            messages.success(request, f"Production batch {batch.batch_no} saved.")
            return redirect("production-list")
    else:
        form = KilnBatchForm()
    return render(request, "core/production_form.html", {"form": form})



@login_required
def party_list(request):
    parties = Party.objects.order_by("name")
    return render(request, "core/party_list.html", {"parties": parties})


@login_required
def party_create(request):
    initial = {}
    requested_type = request.GET.get("party_type")
    allowed_types = {choice[0] for choice in Party.PARTY_TYPES}
    if requested_type in allowed_types:
        initial["party_type"] = requested_type

    if request.method == "POST":
        form = PartyForm(request.POST)
        if form.is_valid():
            party = form.save()
            messages.success(request, f"{party.get_party_type_display()} '{party.name}' saved.")
            return redirect("party-list")
    else:
        form = PartyForm(initial=initial)

    return render(request, "core/party_form.html", {"form": form})


# Custom ERP module pages: these keep users inside the ERP instead of Django Admin.
@login_required
def raw_material_list(request):
    materials = RawMaterial.objects.order_by("name")
    return render(request, "core/raw_material_list.html", {"materials": materials})

@login_required
def raw_material_create(request):
    form = RawMaterialForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Raw material '{obj.name}' saved.")
        return redirect("raw-material-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Add raw material", "back_url": "raw-material-list", "submit_label": "Save raw material"})

@login_required
def purchase_list(request):
    purchases = Purchase.objects.select_related("supplier", "material").order_by("-date", "-id")
    return render(request, "core/purchase_list.html", {"purchases": purchases})

@login_required
def purchase_create(request):
    form = PurchaseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Purchase {obj.voucher_no} saved.")
        return redirect("purchase-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Record raw-material purchase", "back_url": "purchase-list", "submit_label": "Save purchase"})

@login_required
def sale_list(request):
    sales = Sale.objects.select_related("customer").order_by("-date", "-id")
    return render(request, "core/sale_list.html", {"sales": sales})

@login_required
def sale_create(request):
    form = SaleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Sales invoice {obj.invoice_no} saved.")
        return redirect("sale-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Create sales invoice", "back_url": "sale-list", "submit_label": "Save invoice", "form_note": "Sales are priced per 1,000 bricks. Posting an invoice does not yet automatically create a stock movement or accounting journal entry."})

@login_required
def payment_list(request):
    payments = Payment.objects.select_related("party").order_by("-date", "-id")
    return render(request, "core/payment_list.html", {"payments": payments})

@login_required
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Payment voucher {obj.voucher_no} saved.")
        return redirect("payment-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Record payment", "back_url": "payment-list", "submit_label": "Save payment"})

@login_required
def expense_list(request):
    expenses = Expense.objects.select_related("supplier").order_by("-date", "-id")
    return render(request, "core/expense_list.html", {"expenses": expenses})

@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Expense voucher {obj.voucher_no} saved.")
        return redirect("expense-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Record expense", "back_url": "expense-list", "submit_label": "Save expense"})

@login_required
def stock_list(request):
    movements = StockMovement.objects.order_by("-date", "-id")
    stock_balance = sum(m.quantity_change for m in StockMovement.objects.all())
    return render(request, "core/stock_list.html", {"movements": movements, "stock_balance": stock_balance})

@login_required
def stock_movement_create(request):
    form = StockMovementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, "Stock movement saved.")
        return redirect("stock-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Record stock movement", "back_url": "stock-list", "submit_label": "Save stock movement", "form_note": "Use a positive quantity to add bricks and a negative quantity to reduce stock. This is a manual movement; production and sales are not yet posted to stock automatically."})

@login_required
def account_list(request):
    accounts = Account.objects.order_by("code")
    return render(request, "core/account_list.html", {"accounts": accounts})

@login_required
def account_create(request):
    form = AccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, f"Account '{obj.name}' saved.")
        return redirect("account-list")
    return render(request, "core/simple_form.html", {"form": form, "page_title": "Add chart-of-accounts entry", "back_url": "account-list", "submit_label": "Save account"})

@login_required
def reports(request):
    today = timezone.localdate()
    sales = Sale.objects.filter(status="posted")
    purchases = Purchase.objects.all()
    expenses = Expense.objects.all()
    sales_total = sum((obj.total_amount for obj in sales), start=0)
    purchase_total = sum((obj.total_amount for obj in purchases), start=0)
    expense_total = sum((obj.amount + obj.tax_amount for obj in expenses), start=0)
    return render(request, "core/reports.html", {
        "today": today, "sales_count": sales.count(), "sales_total": sales_total,
        "purchase_count": purchases.count(), "purchase_total": purchase_total,
        "expense_count": expenses.count(), "expense_total": expense_total,
        "report_cards": [("Posted sales", sales_total, sales.count()), ("Purchases", purchase_total, purchases.count()), ("Expenses", expense_total, expenses.count())],
    })
