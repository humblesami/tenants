import sys
import traceback
from django.db import utils
from django.conf import settings
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from customers.models import Client, Domain


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            errorMessage += "==================" + er
    return errorMessage


def create_public_tenant():
    domain_url = 'domain.local'
    tenant = Client(schema_name='public',
                    domain_url=domain_url,
                    on_trial=False,
                    paid_until='2024-12-12',
                    name='Schemas Inc.')
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here! on a local server you'll want to use localhost here
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()


def create_real_tenant():
    if not Client.objects.filter(schema_name='public'):
        create_public_tenant()
    t_name = 't1'
    if Client.objects.filter(schema_name=t_name):
        return 'Customer '+t_name+' Already exists'
    domain_url = t_name + '.domain.local'
    tenant = Client(schema_name=t_name,
                    domain_url=domain_url,
                    on_trial=False,
                    paid_until='2024-12-12',
                    name='Schemas '+t_name)
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here!
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    return 'Saved Successfully'


class Page1View(TemplateView):
    template_name = "page1.html"

    def get_context_data(self, **kwargs):
        res = 'Unknown status'
        try:
            res = create_real_tenant()
        except:
            res = produce_exception()
        context = {'p1': res}
        return context


class HomeView(TemplateView):
    template_name = "index_public.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hostname_without_port = remove_www(self.request.get_host().split(':')[0])

        try:
            Client.objects.get(schema_name='public')
        except utils.DatabaseError:
            context['need_sync'] = True
            context['shared_apps'] = settings.SHARED_APPS
            context['tenants_list'] = []
            return context
        except Client.DoesNotExist:
            context['no_public_tenant'] = True
            context['hostname'] = hostname_without_port

        if Client.objects.count() == 1:
            context['only_public_tenant'] = True

        context['tenants_list'] = Client.objects.all()
        return context
