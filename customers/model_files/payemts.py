from django.db import models

from customers.model_files.plans import Plan


class PaymentMethod(models.Model):
    name = models.CharField(max_length=64)


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
    transaction_id = models.CharField(max_length=64, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
