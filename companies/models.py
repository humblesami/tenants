from django.db import models, connection
from django.contrib.auth.models import User
from django_tenants.models import DomainMixin, TenantMixin

from .tools import switch_tenant
from .plans.plan_models import Plan


class ClientTenant(TenantMixin):
    client_email = models.EmailField(null=True, unique=True)
    client_password = models.CharField(max_length=100, null=True)
    client_name = models.CharField(max_length=50, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.RESTRICT, blank=True, null=True, related_name='own_tenant')
    is_active = models.BooleanField(default=True, blank=True)
    users = models.ManyToManyField(User, related_name='tenants', blank=True)
    client_image = models.ImageField(null=True, blank=True, upload_to="profile")
    active_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # default true, schema will be automatically created and
    # synced when it is saved
    auto_create_schema = True
    auto_drop_schema = True
    creating_tenant = 0

    class Meta:
        ordering = ('-featured', '-updated_at')

    def __str__(self):
        return f"{self.client_name}"


    def create_public_user(self):
        public_user = User.objects.create(
            email=self.client_email, username=self.client_email,
            is_active=True
        )
        public_user.set_password(self.client_password)
        public_user.save()
        return public_user

    def save(self, verbosity=1, *args, **kwargs):
        if not self.pk:
            schema_name = ClientTenant.objects.filter(schema_name=self.schema_name)
            if schema_name:
                raise Exception(f'Schema name {self.schema_name} already exists')
            else:
                self.creating_tenant = 1
            self.owner = self.create_public_user()
            if not self.client_name:
                self.client_name = self.schema_name
        return super().save(verbosity=1, *args, **kwargs)


    def create_schema(self, check_if_exists=False, sync_schema=True, verbosity=1):
        res = super().create_schema(check_if_exists=check_if_exists, sync_schema=sync_schema)
        if self.creating_tenant:
            self.creating_tenant = 0
            switch_tenant(self.schema_name)
            new_user = User.objects.create(
                username=self.client_email, email=self.client_email, is_staff=True,
                is_active=True, is_superuser=True
            )
            new_user.set_password(self.client_password)
            new_user.save()
            switch_tenant('public')
        return res


class Domain(DomainMixin):
    pass
