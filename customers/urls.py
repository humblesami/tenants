from django.urls import path
from customers.views import TenantView, Delete, Create

urlpatterns = [
    path('new-tenant', Create.as_view()),
    path('delete-tenant', Delete.as_view()),
    path('', TenantView.as_view(), name="index"),
]