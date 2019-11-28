from django.urls import path
from customers.views import Create, TenantView

urlpatterns = [
    path('new', Create.as_view()),
    path('', TenantView.as_view(), name="index"),
]