from django.contrib import admin
from users.models import TenantUser


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    pass