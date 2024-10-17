from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import Domain, ClientTenant
from .plans.plan_models import Plan, PlanCost
from .subscriptions.subscription_models import Subscription
from .payments.payment_models import Payment, PaymentMethod, PaymentInProgress


class DomainInline(admin.TabularInline):

    model = Domain
    max_num = 1
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk == Domain.objects.order_by('pk').first().pk:
            # Mark all fields as read-only for the first record
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(ClientTenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = (
        "owner",
        'schema_name',
        "client_name",
        "is_active",
        "created_on",
    )
    autocomplete_fields = ['users']
    inlines = [DomainInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk == ClientTenant.objects.order_by('pk').first().pk:
            # Mark all fields as read-only for the first record
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


admin.site.register(Plan)
admin.site.register(PlanCost)
admin.site.register(Payment)
admin.site.register(PaymentInProgress)
admin.site.register(PaymentMethod)
admin.site.register(Subscription)