from django.contrib import admin
from tenant_only.views import Index
from django.urls import path, include

from tenant_tutorial.views import custom_page_not_found

urlpatterns = [
    path('', Index.as_view(), name="index"),
#     path('', include('tenant_only.urls')),
    path('admin/', admin.site.urls),
    path("404", custom_page_not_found),
]