from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django_tenants.utils import get_tenant_model


class TenantUser(User):
    name = models.CharField(max_length=100)
    photo = models.ImageField()

    def save(self, *args, **kwargs):
        if not self.pk:
            tenant_model = get_tenant_model()
            # company = tenant_model.objects.get(schema_name='public')
            # connection.set_tenant(company)
            # ContentType.objects.clear_cache()
            #
            # owner = User.objects.create(username=self.username, is_active=self.is_active, is_stff=self.is_staff)
            # owner.set_password('123')
            # owner.save()
            #
            # company = tenant_model.objects.get(schema_name='public')
            # connection.set_tenant(company)
            # ContentType.objects.clear_cache()

        super(TenantUser, self).save(args, kwargs)


class TableOne(models.Model):
    name = models.CharField(max_length=100)


class TableTwo(models.Model):
    name = models.CharField(max_length=100)
    table_one = models.ForeignKey(TableOne, on_delete=models.CASCADE)
