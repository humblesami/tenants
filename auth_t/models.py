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

    def create_public_user(self, password):
        if connection.tenant.schema_name != 'public':
            connection.set_tenant(self.public_tenant)
            ContentType.objects.clear_cache()
        else:
            public_tenant = connection.tenant
        public_user = User.objects.create(username=self.email, email=self.email, is_active=self.is_active)
        public_user.set_password(password)
        public_user.save()

        self.public_tenant.users.add(public_user)
        self.public_tenant.save()

    my_tenant = None
    public_tenant = None

    def set_tenants(self, my_tenant, public_tenant):
        self.my_tenant = my_tenant
        self.public_tenant = public_tenant


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
                tenant_model = get_tenant_model()
                selected_tenant = connection.tenant()

                if selected_tenant.schema_name != 'public':

                    connection.set_schema_to_public()
                    self.create_public_user(password)
                    connection.set_schema(selected_tenant.schema_name, False)
                else:
                    self.create_public_user(password, selected_tenant)