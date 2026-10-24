from django.contrib import admin
from .models import Party, RawMaterial, Purchase, KilnBatch, StockMovement, Sale, Payment, Expense, Account, JournalEntry, JournalLine

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("name", "party_type", "phone", "gstin", "is_active")
    list_filter = ("party_type", "is_active")
    search_fields = ("name", "phone", "gstin")

@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "reorder_level", "is_active")
    search_fields = ("name",)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("voucher_no", "date", "supplier", "material", "quantity", "unit_rate")
    list_filter = ("date", "material")
    search_fields = ("voucher_no", "supplier__name")

@admin.register(KilnBatch)
class KilnBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_no", "start_date", "kiln_name", "status", "loaded_bricks", "good_bricks", "damaged_bricks")
    list_filter = ("status", "start_date")
    search_fields = ("batch_no", "kiln_name")

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("date", "movement_type", "quantity_change", "reference")
    list_filter = ("movement_type", "date")

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "date", "customer", "brick_quantity", "rate_per_1000", "status")
    list_filter = ("status", "date")
    search_fields = ("invoice_no", "customer__name", "vehicle_no")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("voucher_no", "date", "direction", "party", "amount", "method")
    list_filter = ("direction", "method", "date")
    search_fields = ("voucher_no", "party__name", "reference_no")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("voucher_no", "date", "category", "amount", "paid_from")
    list_filter = ("category", "paid_from", "date")
    search_fields = ("voucher_no", "description")

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "is_active")
    list_filter = ("account_type", "is_active")
    search_fields = ("code", "name")

class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 2

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_no", "date", "narration", "posted")
    list_filter = ("posted", "date")
    search_fields = ("entry_no", "narration")
    inlines = [JournalLineInline]
