from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Customer
from .forms import CustomerForm , SupplierForm
from .models import Supplier


@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by("-created_at")
    return render(request, "crm/customer_list.html", {"customers": customers})


@login_required
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "crm/customer_form.html", {"form": form, "title": "Add Customer"})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "crm/customer_form.html", {"form": form, "title": "Edit Customer"})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect("customer_list")
    return render(request, "crm/customer_confirm_delete.html", {"customer": customer})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by("-created_at")
    return render(request, "crm/supplier_list.html", {"suppliers": suppliers})


@login_required
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()
    return render(request, "crm/supplier_form.html", {"form": form, "title": "Add Supplier"})


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "crm/supplier_form.html", {"form": form, "title": "Edit Supplier"})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        return redirect("supplier_list")
    return render(request, "crm/supplier_confirm_delete.html", {"supplier": supplier})
