from django.contrib import admin
from tenant_only.models import TenantUser, TableOne, TableTwo

admin.site.register(TenantUser)
admin.site.register(TableOne)
admin.site.register(TableTwo)

# @admin.register(TenantUser)
# class TenantUserAdmin(admin.ModelAdmin):
#     pass
#
# @admin.register(TableOne)
# class TableOneAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(TableTwo)
# class TableTwoAdmin(admin.ModelAdmin):
#     pass
