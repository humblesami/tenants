from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from companies.models import ClientTenant, Domain


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Tenant name')
        parser.add_argument('subdomain', type=str, help='Subdomain for tenant')

    def handle(self, *args, **options):
        tenant = ClientTenant(name=options['name'], database_name=f"{options['name']}_db")
        tenant.save()
        domain = Domain(domain=f"{options['subdomain']}.{settings.DOMAIN}", tenant=tenant)
        domain.save()
        # Run migrations for the new database
        call_command('migrate', database=tenant.database_name)
