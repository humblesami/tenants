from django.urls import path
from customers.views import TenantView, Delete, Create
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('new', Create.as_view()),
    path('delete', login_required(Delete.as_view())),
    path('', login_required(TenantView.as_view()), name="index"),
]