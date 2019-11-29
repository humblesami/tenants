from django.contrib import admin
from customers.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass