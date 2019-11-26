from django.conf.urls import url
from django.urls import path
from customer.views import create_tenant

urlpatterns = [
    url('create', create_tenant, name='asa')
]