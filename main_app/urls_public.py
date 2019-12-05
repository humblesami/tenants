from django.urls import path
from django.contrib import admin
from django.conf.urls import include, url
from .views import Login, authenticate_user, logout_user

urlpatterns = [
    url('', include('website.urls')),
    path('accounts/login', Login.as_view()),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('logout', logout_user),
    path('authenticate', authenticate_user),
    url('clients/', include('customers.urls')),
    url('stripe/', include('payments.urls')),
    path('admin/', admin.site.urls),
]
