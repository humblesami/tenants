from django.contrib import admin

from main_app.views import login_page, logout_user
from tenant_only.views import Index
from django.urls import path, include

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('accounts/login', login_page),
    path('logout', logout_user),
    path('admin/', admin.site.urls),
]