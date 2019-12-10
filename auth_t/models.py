from django_tenants.utils import get_tenant_model
from django.contrib.auth.models import User, Group
from django.db import models, connection, transaction
from django.contrib.contenttypes.models import ContentType


class TenantGroup(Group):
    pass


class TenantUser(User):
    name = models.CharField(max_length=100)
    photo = models.ImageField(null=True, blank=True)

    def create_public_user(self, password):
        user_tenant = connection.tenant
        connection.set_schema_to_public()
        tenant_model = get_tenant_model()

        public_tenant = tenant_model.objects.get(schema_name='public')
        connection.set_tenant(public_tenant)
        ContentType.objects.clear_cache()

        public_user = User.objects.filter(email=self.email)
        if not public_user:
            public_user = User.objects.create(username=self.email, email=self.email, is_active=self.is_active)
            public_user.set_password(password)
            public_user.save()
        else:
            public_user = public_user[0]

        user_tenant.users.add(public_user)
        user_tenant.save()

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
        super(TenantUser, self).save(args, kwargs)
        if not self.on_schema_creating:
            self.create_public_user(password)