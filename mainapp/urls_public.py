from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url
from .views import login_page, logout_user

urlpatterns = [
    url('', include('website.urls')),
    url('', include('customers.plans.urls')),
    path('accounts/login', login_page),
    path('logout', logout_user),
    url('clients/', include('customers.urls')),
    url('plans/', include('customers.plans.urls')),
    url('payments/', include('customers.payments.urls')),
    url('subscriptions/', include('customers.subscriptions.urls')),
    path('admin/', admin.site.urls)
]
