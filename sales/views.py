from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

from .models import PurchaseOrder, PurchaseOrderItem
from inventory.models import Product
from crm.models import Supplier
from .forms import PurchaseOrderForm, PurchaseOrderItemForm
from django.contrib.staticfiles.storage import staticfiles_storage

from django.template.loader import render_to_string
from weasyprint import HTML

# PDF IMPORTS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


from django.db.models import Sum
from .models import (
    PurchaseOrder, PurchaseOrderItem,
    Quotation, QuotationItem,
    Invoice, InvoiceItem,
    Receipt,
)
from .forms import (
    PurchaseOrderForm, PurchaseOrderItemForm,
    QuotationForm, QuotationItemForm,
    InvoiceForm, InvoiceItemForm,
    ReceiptForm,
)
from crm.models import Customer



# --------------------------------------------------------
# LIST OF PURCHASE ORDERS
# --------------------------------------------------------
@login_required
def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().order_by("-date")
    return render(request, "sales/po_list.html", {"orders": orders})


# --------------------------------------------------------
# CREATE PURCHASE ORDER
# --------------------------------------------------------
@login_required
def purchase_order_create(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save(commit=False)

            # EXTRA SAFETY:
            supplier_id = request.POST.get("supplier")
            try:
                po.supplier = Supplier.objects.get(id=supplier_id)
            except Supplier.DoesNotExist:
                messages.error(request, "Selected supplier does not exist!")
                return redirect("purchase_order_create")

            po.save()
            return redirect("purchase_order_detail", pk=po.id)

    else:
        form = PurchaseOrderForm()

    return render(request, "sales/po_create.html", {"form": form})



# --------------------------------------------------------
# VIEW PO DETAILS + ITEMS
# --------------------------------------------------------
@login_required
def purchase_order_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    items = PurchaseOrderItem.objects.filter(purchase_order=po)
    products = Product.objects.all()

    return render(
        request,
        "sales/po_detail.html",
        {
            "po": po,
            "items": items,
            "products": products,
        },
    )


# --------------------------------------------------------
# ADD ITEM TO PURCHASE ORDER
# --------------------------------------------------------
@login_required
def purchase_order_add_item(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == "POST":
        form = PurchaseOrderItemForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = po
            item.save()

            # Update PO total
            po.total_amount = po.calculate_total()
            po.save()

            messages.success(request, "Item added successfully!")
            return redirect("purchase_order_detail", pk=pk)
        else:
            messages.error(request, "Invalid form data")
            print("FORM ERRORS:", form.errors)

    # If GET request → redirect back because modal is inside detail page
    return redirect("purchase_order_detail", pk=pk)




# --------------------------------------------------------
# DELETE ITEM FROM PURCHASE ORDER
# --------------------------------------------------------
@login_required
def purchase_order_delete_item(request, po_id, item_id):
    po = get_object_or_404(PurchaseOrder, pk=po_id)
    item = get_object_or_404(PurchaseOrderItem, pk=item_id)
    item.delete()

    # Update totals
    po.total_amount = sum(i.line_total for i in po.items.all())
    po.save()

    messages.warning(request, "Item removed.")
    return redirect("purchase_order_detail", pk=po_id)


# --------------------------------------------------------
# MARK PO AS RECEIVED (UPDATE INVENTORY)
# --------------------------------------------------------
@login_required
def purchase_order_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    if po.status == "Received":
        messages.info(request, "Purchase Order already received.")
        return redirect("purchase_order_detail", pk=pk)

    # update stock
    for item in po.items.all():
        product = item.product
        product.stock += item.quantity
        product.save()

    po.status = "Received"
    po.save()

    messages.success(request, "Inventory updated successfully.")
    return redirect("purchase_order_detail", pk=pk)


# --------------------------------------------------------
# DOWNLOAD PURCHASE ORDER AS PDF
# --------------------------------------------------------
@login_required
def purchase_order_pdf(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    items = po.items.all()

    logo_url = request.build_absolute_uri(
        staticfiles_storage.url("img/logo.png")
    )

    company = {
        "name": "Ed-Tech Africa Innovation College",
        "address": "Barclays House, Main Mall, Gaborone, Botswana",
        "phone": "+267 71 234 567",
        "email": "info@edtechafrica.co.bw",
    }

    return render(request, "sales/po_pdf.html", {
        "po": po,
        "items": items,
        "logo_url": logo_url,
        "company": company,
    })

# --------------------------------------------------------
# SALES DOCUMENTS DASHBOARD (Purchases tab)
# --------------------------------------------------------
@login_required
def sales_documents_dashboard(request):
    total_quotations = Quotation.objects.count()
    total_invoices = Invoice.objects.count()
    total_receipts = Receipt.objects.count()
    total_sales = Receipt.objects.aggregate(total=Sum("amount_paid"))["total"] or 0

    return render(request, "sales/purchases_dashboard.html", {
        "total_quotations": total_quotations,
        "total_invoices": total_invoices,
        "total_receipts": total_receipts,
        "total_sales": total_sales,
    })


# --------------------------------------------------------
# QUOTATIONS
# --------------------------------------------------------
@login_required
def quotation_list(request):
    quotations = Quotation.objects.select_related("customer").order_by("-date")
    return render(request, "sales/quotation_list.html", {"quotations": quotations})


@login_required
def quotation_create(request):
    if request.method == "POST":
        form = QuotationForm(request.POST)
        if form.is_valid():
            quotation = form.save()

            # After saving, redirect to add-items page
            return redirect("quotation_detail", pk=quotation.id)

    else:
        form = QuotationForm()

    return render(request, "sales/quotation_create.html", {"form": form})



@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.items.select_related("product")
    products = Product.objects.all()  # needed for dropdown

    return render(request, "sales/quotation_detail.html", {
        "quotation": quotation,
        "items": items,
        "products": products,
    })



@login_required
def quotation_to_invoice(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)

    invoice = Invoice.objects.create(
        customer=quotation.customer,
        quotation=quotation,
        total_amount=quotation.total_amount,
    )

    for qi in quotation.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product=qi.product,
            quantity=qi.quantity,
            price=qi.price,
        )

    messages.success(request, f"Invoice {invoice.number} created from quotation.")
    return redirect("invoice_detail", pk=invoice.id)


# --------------------------------------------------------
# INVOICES
# --------------------------------------------------------
@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related("customer").order_by("-date")
    return render(request, "sales/invoice_list.html", {"invoices": invoices})


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.select_related("product")
    receipts = invoice.receipts.all()

    return render(request, "sales/invoice_detail.html", {
        "invoice": invoice,
        "items": items,
        "receipts": receipts,
    })


# --------------------------------------------------------
# RECEIPTS (ACTUAL SALES)
# --------------------------------------------------------
@login_required
def receipt_create(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == "POST":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.invoice = invoice
            receipt.save()

            # Update invoice status based on receipts
            if invoice.balance_due() <= 0:
                invoice.status = "Paid"
            else:
                invoice.status = "Partially Paid"
            invoice.save()

            messages.success(request, f"Receipt {receipt.number} created.")
            return redirect("invoice_detail", pk=invoice.id)
    else:
        form = ReceiptForm(initial={"amount_paid": invoice.balance_due()})

    return render(request, "sales/receipt_create.html", {
        "invoice": invoice,
        "form": form,
    })


@login_required
def receipt_list(request):
    receipts = Receipt.objects.select_related("invoice", "invoice__customer").order_by("-date")
    return render(request, "sales/receipt_list.html", {"receipts": receipts})


# --------------------------------------------------------
# SALES SUMMARY (TOTAL ACTUAL SALES)
# --------------------------------------------------------
@login_required
def sales_summary(request):
    total_sales = Receipt.objects.aggregate(total=Sum("amount_paid"))["total"] or 0
    total_invoices = Invoice.objects.count()
    total_customers = Customer.objects.count()

    receipts = Receipt.objects.select_related("invoice", "invoice__customer").order_by("-date")[:20]

    return render(request, "sales/sales_summary.html", {
        "total_sales": total_sales,
        "total_invoices": total_invoices,
        "total_customers": total_customers,
        "recent_receipts": receipts,
    })
    
@login_required
def quotation_convert_to_invoice(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)

    # Create invoice
    invoice = Invoice.objects.create(
        customer=quotation.customer,
        quotation=quotation,
        status="Unpaid",
        total_amount=quotation.total_amount
    )

    # Copy items from quotation → invoice
    for item in quotation.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product=item.product,
            quantity=item.quantity,
            price=item.price  # <-- IMPORTANT
        )

    messages.success(request, "Quotation converted to Invoice successfully!")

    return redirect("invoice_detail", pk=invoice.id)


@login_required
def quotation_add_item(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)

    if request.method == "POST":
        product_id = request.POST.get("product")
        quantity = request.POST.get("quantity")
        price = request.POST.get("unit_price")  # HTML field is unit_price but model uses price

        product = get_object_or_404(Product, id=product_id)

        # Create item correctly
        QuotationItem.objects.create(
            quotation=quotation,
            product=product,
            quantity=quantity,
            price=price,  # <-- correct model field
        )

        # Update totals
        quotation.total_amount = quotation.calculate_total()
        quotation.save()

        messages.success(request, "Item added to quotation.")
        return redirect("quotation_detail", pk=pk)

    return redirect("quotation_detail", pk=pk)


@login_required
def quotation_delete_item(request, pk, item_id):
    quotation = get_object_or_404(Quotation, pk=pk)
    item = get_object_or_404(QuotationItem, pk=item_id)

    item.delete()

    # Update totals
    quotation.total_amount = quotation.calculate_total()
    quotation.save()

    messages.warning(request, "Item removed from quotation.")
    return redirect("quotation_detail", pk=pk)

@login_required
def receipt_create(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == "POST":
        amount_paid = request.POST.get("amount_paid")
        payment_method = request.POST.get("payment_method")
        notes = request.POST.get("notes", "")

        Receipt.objects.create(
            invoice=invoice,
            amount_paid=amount_paid,
            payment_method=payment_method,
            notes=notes
        )

        # Update invoice totals
        invoice.total_amount = invoice.calculate_total()
        invoice.save()

        messages.success(request, "Payment recorded successfully!")
        return redirect("invoice_detail", pk=pk)

    return render(request, "sales/receipt_create.html", {"invoice": invoice})


@login_required
def quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)

    html = render_to_string(
        "sales/pdf/quotation.html",
        {
            "quotation": quotation,
            "company": {
                "name": "Ed-Tech Africa Innovation College",
                "address": "Barclays House, Main Mall, Gaborone, Botswana",
                "phone": "+267 71 234 567",
                "email": "info@edtechafrica.co.bw",
            },
            "title": "QUOTATION",
        }
    )

    pdf = HTML(string=html).write_pdf()
    return HttpResponse(pdf, content_type="application/pdf")


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    html = render_to_string(
        "sales/pdf/invoice.html",
        {
            "invoice": invoice,
            "company": {
                "name": "Ed-Tech Africa Innovation College",
                "address": "Barclays House, Main Mall, Gaborone, Botswana",
                "phone": "+267 71 234 567",
                "email": "info@edtechafrica.co.bw",
            },
            "title": "INVOICE",
        }
    )

    pdf = HTML(string=html).write_pdf()
    return HttpResponse(pdf, content_type="application/pdf")


@login_required
def receipt_pdf(request, invoice_id, receipt_id):
    receipt = get_object_or_404(Receipt, pk=receipt_id)

    html = render_to_string(
        "sales/pdf/receipt.html",
        {
            "receipt": receipt,
            "invoice": receipt.invoice,
            "company": {
                "name": "Ed-Tech Africa Innovation College",
                "address": "Barclays House, Main Mall, Gaborone, Botswana",
                "phone": "+267 71 234 567",
                "email": "info@edtechafrica.co.bw",
            },
            "title": "RECEIPT",
        }
    )

    pdf = HTML(string=html).write_pdf()
    return HttpResponse(pdf, content_type="application/pdf")


@login_required
def purchase_order_delete(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    po.delete()
    messages.success(request, "Purchase Order deleted successfully.")
    return redirect("purchase_order_list")

@login_required
def quotation_delete(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    quotation.delete()
    messages.success(request, "Quotation deleted successfully.")
    return redirect("quotation_list")

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    messages.success(request, "Invoice deleted successfully.")
    return redirect("invoice_list")
