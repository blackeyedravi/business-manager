from django import forms
from .models import (
    PurchaseOrder, PurchaseOrderItem,
    Quotation, QuotationItem,
    Invoice, InvoiceItem,
    Receipt,
)

# existing PurchaseOrderForm, PurchaseOrderItemForm...


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ["customer", "status"]


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["product", "quantity", "price"]


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["customer", "status"]


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["product", "quantity", "price"]


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ["amount_paid", "payment_method", "notes"]

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["supplier"]


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["product", "quantity", "cost_price"]

        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }