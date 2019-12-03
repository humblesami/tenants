from django.db import models
from tenant_users.tenants.models import TenantBase
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantBase):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)


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