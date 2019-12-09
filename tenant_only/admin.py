from django.contrib import admin
from .models import TableOne, TableTwo

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
