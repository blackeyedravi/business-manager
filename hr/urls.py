from django.urls import path
from . import views

urlpatterns = [
    path("", views.placeholder, name="hr_home"),
    path("employees/", views.placeholder, name="employees"),
]
