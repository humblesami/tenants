from django.urls import path
from django.contrib import admin
from main_app.views import tenant_logout
from tenant_only.views import tenant_idex, token_login

urlpatterns = [
    path('', tenant_idex, name="index"),
    path('login/<token>', token_login, name="index"),
    path('logout', tenant_logout),
    path('admin/', admin.site.urls),
]