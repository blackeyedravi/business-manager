# sales/admin.py
from django.contrib import admin
from .models import CustomerOrder, CustomerOrderItem, PurchaseOrder, PurchaseOrderItem

admin.site.register(CustomerOrder)
admin.site.register(CustomerOrderItem)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
