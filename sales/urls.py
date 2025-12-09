from django.urls import path
from . import views

urlpatterns = [

    # PURCHASE ORDERS
    path("orders/", views.purchase_order_list, name="purchase_order_list"),
    path("orders/create/", views.purchase_order_create, name="purchase_order_create"),
    path("orders/<int:pk>/", views.purchase_order_detail, name="purchase_order_detail"),

    # ITEMS
    path("orders/<int:pk>/add-item/", views.purchase_order_add_item, name="purchase_order_add_item"),
    
    path("orders/<int:po_id>/delete-item/<int:item_id>/", views.purchase_order_delete_item, name="purchase_order_delete_item"),

    # MARK AS RECEIVED
    path("orders/<int:pk>/receive/", views.purchase_order_receive, name="purchase_order_receive"),

    # PDF DOWNLOAD
    path("orders/<int:pk>/pdf/", views.purchase_order_pdf, name="purchase_order_pdf"),
    path("purchases/", views.sales_documents_dashboard, name="sales_documents_dashboard"),

    # QUOTATIONS
    path("purchases/quotations/", views.quotation_list, name="quotation_list"),
    path("purchases/quotations/create/", views.quotation_create, name="quotation_create"),
    path("purchases/quotations/<int:pk>/", views.quotation_detail, name="quotation_detail"),
    path("purchases/quotations/<int:pk>/to-invoice/", views.quotation_to_invoice, name="quotation_to_invoice"),

    # INVOICES
    path("purchases/invoices/", views.invoice_list, name="invoice_list"),
    path("purchases/invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),

    # RECEIPTS
    path("purchases/invoices/<int:pk>/receipt/create/", views.receipt_create, name="receipt_create"),
    path("purchases/receipts/", views.receipt_list, name="receipt_list"),

    # SALES SUMMARY
    path("purchases/sales-summary/", views.sales_summary, name="sales_summary"),
    path(
    "purchases/quotations/<int:pk>/convert/",
    views.quotation_convert_to_invoice,
    name="quotation_convert_to_invoice",
),
path(
    "purchases/quotations/<int:pk>/add-item/",
    views.quotation_add_item,
    name="quotation_add_item",
),

path(
    "purchases/quotations/<int:pk>/delete-item/<int:item_id>/",
    views.quotation_delete_item,
    name="quotation_delete_item",
),

path(
    "purchases/invoices/<int:pk>/receipt/create/",
    views.receipt_create,
    name="receipt_create"
),

# QUOTATION PDF
path(
    "purchases/quotations/<int:pk>/pdf/",
    views.quotation_pdf,
    name="quotation_pdf"
),

# INVOICE PDF
path(
    "purchases/invoices/<int:pk>/pdf/",
    views.invoice_pdf,
    name="invoice_pdf"
),

# RECEIPT PDF
path(
    "purchases/invoices/<int:invoice_id>/receipt/<int:receipt_id>/pdf/",
    views.receipt_pdf,
    name="receipt_pdf"
),

path("purchase-orders/<int:pk>/delete/", views.purchase_order_delete, name="purchase_order_delete"),
path("quotations/<int:pk>/delete/", views.quotation_delete, name="quotation_delete"),
path("invoices/<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),

]
