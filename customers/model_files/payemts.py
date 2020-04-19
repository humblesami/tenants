from django.db import models


class PaymentMethod(models.Model):
    name = models.CharField(max_length=64)


class Payment(models.Model):
    request = models.CharField(max_length=64)
    amount = models.PositiveIntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    medium = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=128)

    def save(self, kw, **args):
        #add to Subscription
        super(Payment, self).save(kw, args)

