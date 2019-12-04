from django.contrib import admin
from customers.models import Client
from tenant_only.models import TenantUser

admin.site.register(Client)
admin.site.register(TenantUser)
