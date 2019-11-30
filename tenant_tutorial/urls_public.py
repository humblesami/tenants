from django.urls import path
from django.conf.urls import include, url

from tenant_tutorial.views import HomeView
from django.contrib import admin

urlpatterns = [
    path('', include('customers.urls')),
    path('admin/', admin.site.urls),
]
