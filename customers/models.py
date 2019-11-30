from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    schema = models.CharField(max_length=100)
    description = models.TextField(max_length=200, default='')
    created_on = models.DateField(auto_now_add=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='superuser')
    users = models.ManyToManyField(User)

    def delete_tenant(self):
        self.delete()
        # drop_schema()


class Domain(DomainMixin):
    pass


class Plan(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default='')


class PlanCost(models.Model):
    plan_id = models.ForeignKey(Plan, on_delete=models.CASCADE)
    cost = models.IntegerField()
    from_date = models.DateField(default=None)


class ClientPlan(models.Model):
    active = models.BooleanField(default=True)
    plan_id = models.ForeignKey(Plan, on_delete=models.CASCADE)
    cost_id = models.ForeignKey(PlanCost, on_delete=models.CASCADE)
    discount = models.IntegerField()
    start_date = models.DateField()
    end_data = models.DateField()