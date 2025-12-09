from django.db import models
from crm.models import Customer, Supplier
from inventory.models import Product


# --------------------------------------------------------
# CUSTOMER ORDER (not related to purchase orders)
# --------------------------------------------------------
class CustomerOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="Pending")

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"


class CustomerOrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # sale price at time

    def line_total(self):
        return self.quantity * self.price


# --------------------------------------------------------
# PURCHASE ORDER
# --------------------------------------------------------
class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Received", "Received")],
        default="Pending",
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def calculate_total(self):
        return sum(item.line_total() for item in self.items.all())

    def __str__(self):
        return f"PO #{self.id} - {self.supplier.name}"


# --------------------------------------------------------
# PURCHASE ORDER ITEMS
# --------------------------------------------------------
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.quantity * self.cost_price


# --------------------------------------------------------
# QUOTATION
# --------------------------------------------------------
class Quotation(models.Model):
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Sent", "Sent"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.number or 'Quotation'} - {self.customer.name}"

    def calculate_total(self):
        return sum(item.line_total for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.number:
            last = Quotation.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.number = f"Q-{next_id:04d}"
        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.price


# --------------------------------------------------------
# INVOICE
# --------------------------------------------------------
class Invoice(models.Model):
    STATUS_CHOICES = [
        ("Unpaid", "Unpaid"),
        ("Partially Paid", "Partially Paid"),
        ("Paid", "Paid"),
        ("Cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quotation = models.ForeignKey(
        Quotation, null=True, blank=True, on_delete=models.SET_NULL
    )
    date = models.DateField(auto_now_add=True)
    number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Unpaid")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.number or 'Invoice'} - {self.customer.name}"

    def calculate_total(self):
        return sum(item.line_total for item in self.items.all())

    def amount_received(self):
        from django.db.models import Sum
        return self.receipts.aggregate(total=Sum("amount_paid"))["total"] or 0

    def balance_due(self):
        return self.total_amount - self.amount_received()

    def save(self, *args, **kwargs):
        if not self.number:
            last = Invoice.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.number = f"INV-{next_id:04d}"
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.price


# --------------------------------------------------------
# RECEIPT (ACTUAL SALES)
# --------------------------------------------------------
class Receipt(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("Bank Transfer", "Bank Transfer"),
        ("Mobile Money", "Mobile Money"),
    ]

    invoice = models.ForeignKey(
        Invoice, related_name="receipts", on_delete=models.CASCADE
    )
    date = models.DateField(auto_now_add=True)
    number = models.CharField(max_length=20, unique=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="Cash"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.number or 'Receipt'} - {self.invoice.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            last = Receipt.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.number = f"RC-{next_id:04d}"
        super().save(*args, **kwargs)
