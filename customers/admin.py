from django.contrib import admin
from customers.models import Client
from customers.model_files.subscription import Subscription
from customers.model_files.payemts import Payment, PaymentMethod
from customers.model_files.plans import Plan, PlanCost


admin.site.register(Client)
admin.site.register(Plan)
admin.site.register(PlanCost)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(Subscription)