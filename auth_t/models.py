from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection, transaction
from django_tenants.utils import get_tenant_model


class TenantGroup(Group):
    pass


class TenantUser(User):
    name = models.CharField(max_length=100)
    photo = models.ImageField(null=True, blank=True)

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
                selected_tenant = connection.get_tenant()

                # going at public tenant
                public_tenant = tenant_model.objects.get(schema_name='public')
                connection.set_tenant(public_tenant)
                ContentType.objects.clear_cache()

                tenant_user = User.objects.create(username=self.email, email=self.email, is_active=self.is_active)
                tenant_user.set_password(password)
                tenant_user.save()

                public_tenant.users.add(tenant_user)
                public_tenant.save()

                selected_tenant.users.add(tenant_user)
                selected_tenant.save()

                #back to tenant
                connection.set_tenant(selected_tenant)
                ContentType.objects.clear_cache()