from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url
# from django.views.defaults import page_not_found
from tenant_tutorial.views import custom_page_not_found

urlpatterns = [
    url('', include('customers.urls')),
    path('admin/', admin.site.urls),
    path("404", custom_page_not_found),
]
