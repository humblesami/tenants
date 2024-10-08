from django_tenants.admin import TenantAdminMixin

from .models import Domain, ClientTenant
from django.contrib import admin
from companies.model_files.subscription import Subscription
from companies.model_files.payemts import Payment, PaymentMethod, PaymentInProgress
from companies.model_files.plans import Plan, PlanCost



class DomainInline(admin.TabularInline):

    model = Domain
    max_num = 1

@admin.register(ClientTenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
        list_display = (
            "owner",
            'schema_name',
            "client_name",
            "is_active",
            "created_on",
        )
        inlines = [DomainInline]

admin.site.register(Plan)
admin.site.register(PlanCost)
admin.site.register(Payment)
admin.site.register(PaymentInProgress)
admin.site.register(PaymentMethod)
admin.site.register(Subscription)