from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(default='')
    cost = models.IntegerField(default=0)
    days = models.IntegerField(default=0)

    
class PlanCost(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    cost = models.IntegerField(default=0)
    from_date = models.DateField(default=None)
    days = models.IntegerField(default=0)

    def save(self, kw, **args):
        creating = False
        if not self.pk:
            creating = True
        super(PlanCost, self).save(kw, args)
        if creating:
            self.plan.cost = self.cost
            self.plan.days = self.days
            self.plan.save()


class PlanRequest(models.Model):
    name = models.CharField(max_length=64)
    email = models.EmailField()
    processed = models.BooleanField(default=False)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        super(PlanRequest, self).save(*args, **kwargs)
        


class Subscription(models.Model):
    active = models.BooleanField(default=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    plan_cost = models.ForeignKey(PlanCost, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)
    start_date = models.DateField()
    end_data = models.DateField()