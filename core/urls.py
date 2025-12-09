from django.contrib import admin
from django.urls import path, include
from accounts.views import dashboard
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    
    path("crm/", include("crm.urls")),
    path("inventory/", include("inventory.urls")),
    path("sales/", include("sales.urls")),
    
    path("hr/", include("hr.urls")),
    path("", views.dashboard, name="dashboard"),
]
