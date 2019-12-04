from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url

urlpatterns = [
    url('', include('website.urls')),
    url('clients/', include('customers.urls')),
    url('stripe/', include('my_stripe.urls')),
    path('admin/', admin.site.urls),
]
