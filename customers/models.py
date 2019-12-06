from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=512, blank=True, default='')
    created_on = models.DateField(auto_now_add=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='superuser')
    users = models.ManyToManyField(User)
    domain_url = models.CharField(max_length=64, default='')

    def __str__(self):
        return self.domain_url + '-' + str(self.id)

    def delete_tenant(self):
        self.delete(force_drop=True)