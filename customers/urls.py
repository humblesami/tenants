from django.urls import path

from customers.views import Create

urlpatterns = [
    path('create', Create.as_view())
]