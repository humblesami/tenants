from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url

urlpatterns = [
    url('', include('customers.urls')),
    path('admin/', admin.site.urls),
]
