from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import Domain, ClientTenant, Subscription, Payment, \
    PaymentMethod, ClientUser, AppCost, AppModule, Duration, UserWindow


class DomainInline(admin.TabularInline):

    model = Domain
    max_num = 1
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields] if obj else []

class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ['cost']


class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = (
        "owner",
        'schema_name',
        "is_active",
        "created_on",
    )
    autocomplete_fields = ['users']
    inlines = [DomainInline]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            return [field for field in fields if field not in ['client_password', 'users']]
        return fields

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []
        editable_fields = ['client_name']
        return [field.name for field in self.model._meta.fields if field.name not in editable_fields]


# admin.site.register(Plan)
# admin.site.register(PlanCost)
# admin.site.register(PaymentInProgress)
admin.site.register(AppModule)
admin.site.register(Duration)
admin.site.register(UserWindow)
admin.site.register(AppCost)
admin.site.register(Payment)
admin.site.register(ClientUser)
admin.site.register(PaymentMethod)
admin.site.register(ClientTenant, TenantAdmin)
admin.site.register(Subscription, SubscriptionAdmin)