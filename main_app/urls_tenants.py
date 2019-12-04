from django.contrib import admin
from tenant_only.views import Index
from django.urls import path, include

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('admin/', admin.site.urls),
]