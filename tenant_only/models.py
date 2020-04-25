from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django_tenants.utils import get_tenant_model


class TenantUser(User):
    name = models.CharField(max_length=100)
    photo = models.ImageField()
    is_schema_owner = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        user = super(TenantUser, self).save(args, kwargs)
        if not self.is_schema_owner:
            user_tenant = connection.get_tenant()
            connection.set_schema_to_public()
            public_user = User.objects.create(username=self.username, is_active=True)
            public_user.set_password(self.password)
            public_user.save()
            connection.set_tenant(user_tenant)
            ContentType.objects.clear_cache()
        return user


class TableOne(models.Model):
    name = models.CharField(max_length=100)


class TableTwo(models.Model):
    name = models.CharField(max_length=100)
    table_one = models.ForeignKey(TableOne, on_delete=models.CASCADE)


class UploadFile(models.Model):
    filename = models.FileField(upload_to='uploads/')
