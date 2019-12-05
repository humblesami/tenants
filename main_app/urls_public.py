from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url
from .views import Login, authenticate_user, logout_user

urlpatterns = [
    url('', include('website.urls')),
    url('', include('customers.plans.urls')),
    path('accounts/login', Login.as_view()),
    path('logout', logout_user),
    path('authenticate', authenticate_user),
    url('clients/', include('customers.urls')),
    url('plans/', include('customers.plans.urls')),
    url('payments/', include('customers.payments.urls')),
    url('subscriptions/', include('customers.subscriptions.urls')),
    path('admin/', admin.site.urls)
]
