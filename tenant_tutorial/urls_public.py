from django.urls import path
from django.conf.urls import include, url
from tenant_tutorial.views import HomeView
from django.contrib import admin
from . import views

urlpatterns = [
    path('', HomeView.as_view()),
    path('admin/', admin.site.urls),
    url('customers/', include('customers.urls')),
    path('paymentPage/', views.paymentPage, name='paymentPage'),
    path('paymentCharge/', views.paymentCharge, name='paymentCharge'),
    path('chargelist/', views.chargeList, name='paymentlist'),
]
