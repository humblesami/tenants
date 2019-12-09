from django.db import models

from customers.model_files.plans import Plan


class PaymentMethod(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name


class Payment(models.Model):
    amount = models.PositiveIntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=128)

class PaymentInProgress(models.Model):
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    company = models.CharField(max_length=32)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)

    email = models.EmailField(null=True)
    error = models.TextField(default='')
    transaction_id = models.CharField(max_length=64, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return self.company + " - " + self.method.name + " - " + str(self.amount)