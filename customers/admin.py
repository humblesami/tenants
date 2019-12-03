from django.contrib import admin

from customers.models import Client, Domain
from tenant_only.models import TenantUser

admin.site.register(Client)
admin.site.register(Domain)
admin.site.register(TenantUser)
