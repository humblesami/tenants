from django.contrib import admin

from customers.models import Client, Domain

admin.site.register(Client)
admin.site.register(Domain)