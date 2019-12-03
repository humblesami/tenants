from django.urls import path
from django.conf.urls import include, url
from tenant_tutorial.views import HomeView
from django.contrib import admin
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('customers.urls')),
    path('stripe/', include('my_stripe.urls'))
]
