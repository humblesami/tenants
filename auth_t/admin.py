from django.contrib import admin
from .models import TenantUser, TenantGroup

admin.site.register(TenantUser)
admin.site.register(TenantGroup)