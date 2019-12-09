from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection, transaction
from django_tenants.utils import get_tenant_model

from customers.models import Client


class TenantGroup(Group):
    pass


class TenantUser(User):
    name = models.CharField(max_length=100)
    photo = models.ImageField(null=True, blank=True)

    def create_public_user(self, password, public_tenant, user_tenant):
        connection.set_tenant(public_tenant)
        ContentType.objects.clear_cache()

        public_user = User.objects.create(username=self.email, email=self.email, is_active=self.is_active)
        public_user.set_password(password)
        public_user.save()

        self.public_tenant.users.add(public_user)
        self.public_tenant.save()

        self.on_schema_creating = False
        connection.set_tenant(user_tenant)
        ContentType.objects.clear_cache()

    on_schema_creating = False
    def save(self, *args, **kwargs):
        creating = False
        password = self.password
        if not self.pk:
            creating = True
        if self.email:
            self.username = self.email
        elif self.username:
            self.email = self.username
        if not creating:
            super(TenantUser, self).save(args, kwargs)
        else:
            with transaction.atomic():
                super(TenantUser, self).save(args, kwargs)
                if not self.on_schema_creating:
                    user_tenant = connection.tenant
                    connection.set_schema_to_public()
                    tenant_model = get_tenant_model()
                    public_tenant = tenant_model.objects.filter(schema_name='public')
                    self.create_public_user(password, public_tenant, user_tenant)