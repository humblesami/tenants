from django.urls import path
from django.conf.urls import include, url

from customers.views import CreateCustomer
from tenant_tutorial.views import HomeView
from django.contrib import admin

urlpatterns = [
    path('', HomeView.as_view()),
    path('admin/', admin.site.urls),
    path('abcg', CreateCustomer.as_view()),
    url(r'customers/', include('customers.urls')),
]
