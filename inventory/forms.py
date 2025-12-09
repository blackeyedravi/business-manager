from django import forms
from .models import Product
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "animal_type",
            "meat_type",
            "weight_kg",
            "cost_price_per_kg",
            "selling_price_per_kg",
            "stock",
        ]

        widgets = {
            "animal_type": forms.Select(attrs={"class": "form-select"}),
            "meat_type": forms.Select(attrs={"class": "form-select"}),
            "weight_kg": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "cost_price_per_kg": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "selling_price_per_kg": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
        }

def product_print_label(request, pk):
    product = Product.objects.get(pk=pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="product_{pk}_label.pdf"'

    p = canvas.Canvas(response, pagesize=A6)
    w, h = A6

    p.setFont("Helvetica-Bold", 12)
    p.drawString(10, h - 20, product.name)

    p.setFont("Helvetica", 10)
    p.drawString(10, h - 40, f"Animal: {product.animal_type}")
    p.drawString(10, h - 55, f"Weight: {product.weight} kg")
    p.drawString(10, h - 70, f"Price: P{product.selling_price}")

    p.drawString(10, h - 90, f"SKU: {product.sku}")

    p.showPage()
    p.save()
    return response