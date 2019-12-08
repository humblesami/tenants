from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    cost = models.PositiveIntegerField()
    days = models.PositiveIntegerField()

    
class PlanCost(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    cost = models.IntegerField()
    date_time = models.DateField(auto_now_add=True)
    days = models.IntegerField()

    def save(self, kw, **args):
        creating = False
        if not self.pk:
            creating = True
        else:
            return
        super(PlanCost, self).save(kw, args)
        if creating:
            self.plan.cost = self.cost
            self.plan.days = self.days
            self.plan.save()