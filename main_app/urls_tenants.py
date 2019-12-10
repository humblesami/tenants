from django.conf.urls import url
from django.contrib import admin

from main_app.views import tenant_logout
from tenant_only.views import Index, TokenIndex
from django.urls import path, include

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('login/<token>', TokenIndex.as_view(), name="index"),
    url('clients/', include('customers.urls')),
    path('logout', tenant_logout),
    path('admin/', admin.site.urls),
]