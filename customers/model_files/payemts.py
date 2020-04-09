from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint

from customers.model_files.subscription import Subscription
from customers.model_files.plans import Plan
from mainapp.ws_methods import diff_seconds


class PaymentMethod(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name


class Payment(models.Model):
    amount = models.PositiveIntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=128)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)


class PaymentInProgress(models.Model):
    amount = models.PositiveIntegerField()
    company = models.CharField(max_length=32)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)

    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, null=True)
    email = models.EmailField(null=True)
    error = models.TextField(default='')
    transaction_id = models.CharField(max_length=64, null=True)

    date_time = models.DateTimeField(auto_now_add=True)

    UniqueConstraint(fields=['company'], name='unique_company_payment_promise')

    def save(self, *args, **kwargs):
        creating = True
        if self.pk:
            creating = False
        if creating:
            obj = PaymentInProgress.objects.filter(company=self.company)
            if obj:
                obj = obj[0]
                if obj.check_company():
                    raise ValidationError('Company already exists')
        return super(PaymentInProgress, self).save(args, kwargs)

    @classmethod
    def company_exists(cls, company):
        obj = PaymentInProgress.objects.filter(company=company)
        if not obj:
            return False
        else:
            obj = obj[0]
            return obj.check_company(company)

    def check_company(self, company=None):
        obj = self
        if company and obj.company != company:
            return False
        if not obj.transaction_id:
            diff = diff_seconds(obj.date_time)
            if diff > 6000:
                return False
            else:
                return True
        else:
            return True

    def __str__(self):
        title = self.company + ' - ' + str(self.amount) + ' - ' + str(self.date_time)
        if self.method:
            title += " - " + self.method.name
        return title