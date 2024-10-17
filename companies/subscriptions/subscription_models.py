from django.db import models
from ..plans.plan_models import Plan, PlanCost


class Subscription(models.Model):
    active = models.BooleanField(default=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    plan_cost = models.ForeignKey(PlanCost, on_delete=models.CASCADE)
    amount = models.IntegerField()
    discount = models.IntegerField(default=0)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    def days_left(self):
        return 0