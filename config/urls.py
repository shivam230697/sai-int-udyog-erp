from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("production/", views.production_list, name="production-list"),
    path("production/new/", views.production_create, name="production-create"),
    path("parties/", views.party_list, name="party-list"),
    path("parties/new/", views.party_create, name="party-create"),
    path("reports/", views.reports, name="reports"),
    path("accounts/new/", views.account_create, name="account-create"),
    path("accounts/", views.account_list, name="account-list"),
    path("stock/new/", views.stock_movement_create, name="stock-create"),
    path("stock/", views.stock_list, name="stock-list"),
    path("expenses/new/", views.expense_create, name="expense-create"),
    path("expenses/", views.expense_list, name="expense-list"),
    path("payments/new/", views.payment_create, name="payment-create"),
    path("payments/", views.payment_list, name="payment-list"),
    path("sales/new/", views.sale_create, name="sale-create"),
    path("sales/", views.sale_list, name="sale-list"),
    path("purchases/new/", views.purchase_create, name="purchase-create"),
    path("purchases/", views.purchase_list, name="purchase-list"),
    path("raw-materials/new/", views.raw_material_create, name="raw-material-create"),
    path("raw-materials/", views.raw_material_list, name="raw-material-list"),
]
