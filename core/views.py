from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from datetime import date

from inventory.models import Product

from django.db.models.functions import TruncMonth

from sales.models import Invoice, Receipt, Quotation, PurchaseOrder

@login_required
def dashboard(request):
    # -------- TOP KPIs --------

    # 1) Actual money received (from receipts)
    total_sales = (
        Receipt.objects.aggregate(total=Sum("amount_paid"))["total"] or 0
    )

    # 2) Invoices
    total_invoices = Invoice.objects.count()
    unpaid_invoices = Invoice.objects.filter(
        status__in=["Unpaid", "Partially Paid"]
    ).count()

    # 3) Quotations
    total_quotations = Quotation.objects.count()
    pending_quotations = Quotation.objects.filter(
        status__in=["Draft", "Sent"]
    ).count()

    # 4) Purchases (only POs that are Received)
    total_purchases = (
        PurchaseOrder.objects.filter(status="Received")
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )
    pending_purchase_orders = PurchaseOrder.objects.filter(
        status="Pending"
    ).count()

    # -------- Low stock products (using your new Product model) --------
    LOW_STOCK_THRESHOLD = 5
    low_stock_products = (
        Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD)
        .order_by("stock")[:5]
    )

    # -------- Recent activity --------
    recent_invoices = Invoice.objects.order_by("-date")[:5]
    recent_quotations = Quotation.objects.order_by("-date")[:5]
    recent_receipts = Receipt.objects.order_by("-date")[:5]

    # -------- Charts: Sales & Purchases by month --------

    # Sales by month from receipts
    sales_by_month = (
        Receipt.objects
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount_paid"))
        .order_by("month")
    )
    sales_labels = [
        s["month"].strftime("%b %Y") for s in sales_by_month if s["month"]
    ]
    sales_values = [float(s["total"]) for s in sales_by_month]

    # Purchases by month from POs
    purchases_by_month = (
        PurchaseOrder.objects.filter(status="Received")
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )
    purchase_labels = [
        p["month"].strftime("%b %Y") for p in purchases_by_month if p["month"]
    ]
    purchase_values = [float(p["total"]) for p in purchases_by_month]

    context = {
        # KPIs
        "total_sales": total_sales,
        "total_invoices": total_invoices,
        "unpaid_invoices": unpaid_invoices,
        "total_quotations": total_quotations,
        "pending_quotations": pending_quotations,
        "total_purchases": total_purchases,
        "pending_purchase_orders": pending_purchase_orders,
        "low_stock_products": low_stock_products,

        # Recent
        "recent_invoices": recent_invoices,
        "recent_quotations": recent_quotations,
        "recent_receipts": recent_receipts,

        # Charts
        "sales_labels": sales_labels,
        "sales_values": sales_values,
        "purchase_labels": purchase_labels,
        "purchase_values": purchase_values,
    }

    # IMPORTANT: template name matches your structure
    return render(request, "dashboard.html", context)