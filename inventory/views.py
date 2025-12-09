from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Product
from .forms import ProductForm


from reportlab.lib.pagesizes import A4

from django.http import HttpResponse
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas



@login_required
def product_list(request):
    products = Product.objects.all().order_by("-created_at")
    return render(request, "inventory/product_list.html", {"products": products})


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "inventory/product_form.html", {"form": form, "title": "Add Product"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Edit Product"})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "inventory/product_confirm_delete.html", {"product": product})



def product_label_pdf(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # 80mm x 50mm label
    width = 80 * mm
    height = 50 * mm

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="label_{product.code}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=(width, height))

    y = height - 10

    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2, y, "MEAT PRODUCT LABEL")
    y -= 10

    p.setFont("Helvetica", 9)
    p.drawString(5, y, f"Animal: {product.animal_type}")
    y -= 8
    p.drawString(5, y, f"Meat: {product.meat_type}")
    y -= 8
    p.drawString(5, y, f"Weight: {product.weight_kg} kg")
    y -= 8
    p.drawString(5, y, f"Price/kg: P{product.selling_price_per_kg}")
    y -= 8
    p.drawString(5, y, f"Total: P{product.total_selling_price}")
    y -= 8
    p.drawString(5, y, f"Packed: {product.created_at.date()}")

    y -= 10
    p.setFont("Helvetica", 7)
    p.drawString(5, y, f"ID: {str(product.code)[:8]}")

    p.save()
    return response

@login_required
def product_print_label(request, pk):
    """
    Generate a small PDF label for sticking on the animal/meat pack.
    """
    product = get_object_or_404(Product, pk=pk)

    # Small label size (in points: 1 point = 1/72 inch)
    # You can adjust this size if needed
    label_width = 250
    label_height = 140

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="label_{product.id}.pdf"'

    p = canvas.Canvas(response, pagesize=(label_width, label_height))

    y = label_height - 20

    # Product / Animal name
    p.setFont("Helvetica-Bold", 12)
    p.drawString(10, y, (product.name or "").upper())
    y -= 18

    p.setFont("Helvetica", 10)

    # Animal type (if you added this field)
    if hasattr(product, "animal_type") and product.animal_type:
        p.drawString(10, y, f"Animal: {product.animal_type}")
        y -= 14

    # SKU / code if available
    if hasattr(product, "sku") and product.sku:
        p.drawString(10, y, f"Code: {product.sku}")
        y -= 14

    # Price in Pula
    if hasattr(product, "selling_price") and product.selling_price is not None:
        p.drawString(10, y, f"Price: P{product.selling_price}")
        y -= 14

    # You can add more fields later (weight, meat type, packed date etc.)

    p.showPage()
    p.save()
    return response