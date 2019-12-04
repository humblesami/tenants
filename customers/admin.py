from django.contrib import admin
from customers.models import Client
from customers.model_files.plans import Plan, PlanCost, PlanRequest, Subscription

admin.site.register(Client)
admin.site.register(Plan)
admin.site.register(PlanCost)
admin.site.register(PlanRequest)
admin.site.register(Subscription)