from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default='')
    cost = models.IntegerField()
    days = models.IntegerField()


class PlanCost(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    cost = models.IntegerField()
    from_date = models.DateField(default=None)
    days = models.IntegerField()

    def save(self, kw, **args):
        super(PlanCost, self).save(kw, args)
        self.plan.cost = self.cost
        self.plan.days = self.days
        self.plan.save()


class Request(models.Model):
    name = models.CharField(max_length=64)
    email = models.EmailField()
    processed = models.BooleanField(default=False)
    plan_id = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)


class Subscription(models.Model):
    active = models.BooleanField(default=True)
    plan_id = models.ForeignKey(Plan, on_delete=models.CASCADE)
    cost_id = models.ForeignKey(PlanCost, on_delete=models.CASCADE)
    discount = models.IntegerField()
    start_date = models.DateField()
    end_data = models.DateField()