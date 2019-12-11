from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'setting up migrations and permissions against groups'

    def add_arguments(self, parser):
        parser.add_argument('-m', '--migrations', action='store_true', help='make migrations and migrate')
        parser.add_argument('-f', '--fixtures', action='store_true', help='load fixtures')
        parser.add_argument('-sp', '--set_permissions', action='store_true', help='set permissions to the groups')

    def handle(self, *args, **kwargs):
        migrations = kwargs['migrations']
        fixtures = kwargs['fixtures']
        set_permissions = kwargs['set_permissions']
        if migrations:
            call_command('makemigrations')
            call_command('migrate')
        if set_permissions:
            call_command('init_permissions', fixtures=fixtures)