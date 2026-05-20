from django.urls import path

from . import views

app_name = "gdpr"

urlpatterns = [
    path("account/", views.account, name="account"),
    path("export/", views.export_my_data, name="export"),
    path("delete/", views.delete_my_data, name="delete"),
]