from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from crm.models import Customer, Supplier
from inventory.models import Product
from sales.models import CustomerOrder, PurchaseOrder
from hr.models import Employee

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    context = {
        "customers_count": Customer.objects.count(),
        "suppliers_count": Supplier.objects.count(),
        "products_count": Product.objects.count(),
        "orders_count": CustomerOrder.objects.count(),
        "purchases_count": PurchaseOrder.objects.count(),
        "employees_count": Employee.objects.count(),
    }
    return render(request, "dashboard.html", context)
