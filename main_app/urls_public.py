from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url
from .views import Login, authenticate_user, logout_user

urlpatterns = [
    url('', include('website.urls')),
    path('login', Login.as_view()),
    path('logout', logout_user),
    path('authenticate', authenticate_user),
    url('clients/', include('customers.urls')),
    url('stripe/', include('my_stripe.urls')),
    path('admin/', admin.site.urls),
]
