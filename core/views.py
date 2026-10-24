from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import KilnBatchForm
from .models import KilnBatch, Sale, StockMovement, Expense, Purchase


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
