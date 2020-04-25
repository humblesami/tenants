from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url

from main_app.views import logout_view, login_view

urlpatterns = [
    url('', include('website.urls')),
    url('clients/', include('customers.urls')),
    path('login', login_view),
    path('logout', logout_view),
    url('stripe/', include('my_stripe.urls')),
    path('admin/', admin.site.urls),
]
