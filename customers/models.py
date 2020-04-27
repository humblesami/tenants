from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin

from main_app.ws_methods import get_company_url
from .model_files import payemts, plans


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200, default='')
    created_on = models.DateField(auto_now_add=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='superuser')
    users = models.ManyToManyField(User)

    @property
    def domain_url(self):
        res = get_company_url(self.schema_name)
        return res

    def __str__(self):
        return self.domain_url + '-' + str(self.id)

    def delete_tenant(self):
        self._drop_schema(force_drop=True)
        self.users.all().delete()
        self.delete()