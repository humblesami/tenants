from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    url('', include('tenant_only.urls')),
    path('admin/', admin.site.urls),
]