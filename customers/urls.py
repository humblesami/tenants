from django.urls import path
from customers.views import Create, TenantView, Delete

urlpatterns = [
    path('new', Create.as_view()),
    path('delete', Delete.as_view()),
    path('', TenantView.as_view(), name="index"),
]