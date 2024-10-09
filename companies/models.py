from django.db import models, connections
from django.contrib.auth.models import User
from django_tenants.models import DomainMixin, TenantMixin
from django_tenants.utils import get_tenant_database_alias, schema_exists
from .model_files.plans import Plan


class ClientTenant(TenantMixin):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='own_tenant')
    users = models.ManyToManyField(User,  related_name='tenants', blank=True)
    client_name = models.CharField(max_length=50)
    client_image = models.ImageField(null=True, blank=True, upload_to="profile")
    active_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    featured = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=False, blank=True)
    created_on = models.DateField(auto_now_add=True)
    # default true, schema will be automatically created and
    # synced when it is saved
    auto_create_schema = True

    """
    USE THIS WITH CAUTION!
    Set this flag to true on a parent class if you want the schema to be
    automatically deleted if the tenant row gets deleted.
    """
    auto_drop_schema = True


    class Meta:
        ordering = ('-featured', '-updated_at')

    def __str__(self):
        return f"{self.client_name}"

    def create_schema(self, check_if_exists=False, sync_schema=True, verbosity=1):
        if check_if_exists and schema_exists(self.schema_name):
            return False
        super().create_schema(check_if_exists=check_if_exists, sync_schema=sync_schema, verbosity=verbosity)
        created = schema_exists(self.schema_name)
        if created:
            try:
                connection = connections[get_tenant_database_alias()]
                connection.set_schema(self.schema_name)
                User.objects.create_superuser('admin', 'aa@aa.aa', '123')
                connection.set_schema_to_public()
            except Exception as ex:
                a = str(ex)
                a = 1


class Domain(DomainMixin):
    pass
