from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("add/", views.product_create, name="product_create"),
    path("<int:pk>/edit/", views.product_update, name="product_update"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
    path(
    "products/<int:pk>/label/",
    views.product_label_pdf,
    name="product_label_pdf"
),
path("products/<int:pk>/print/", views.product_print_label, name="product_print"),
path("<int:pk>/print-label/", views.product_print_label, name="product_print_label"),

]
