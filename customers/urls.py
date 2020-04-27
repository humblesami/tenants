from django.urls import path
from django.contrib.auth.decorators import login_required
from customers.views import TenantView, Delete, Create, my_companies

urlpatterns = [
    path('new', Create.as_view()),
    path('my-companies', my_companies),
    path('delete', login_required(Delete.as_view())),
    path('', login_required(TenantView.as_view()), name="index"),
]
