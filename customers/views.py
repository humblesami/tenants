import sys
import traceback
from customers.models import Client, Domain
from django.views.generic import TemplateView
from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant
from users.models import TenantUser
from tenant_users.tenants.tasks import provision_tenant
from django.db import transaction


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            errorMessage += "==================" + er
    return errorMessage

class CreateCustomer(TemplateView):
    template_name = "abc.html"

    def get_context_data(self, **kwargs):
        res = 'Unknown status'    
        try:
            with transaction.atomic():
                try:
                    create_public_tenant("localhost:8000", "admin@localhost")
                    TenantUser.objects.create_superuser(email="superuser@localhost", password='123', is_active=True)
                except:
                    pass
                TenantUser.objects.create_user(email="tenant2@localhost", password=123, is_active=True, is_staff=True)
                provision_tenant("Tenant2", "tenant2", "tenant2@localhost", is_staff=True)
                res = "Created"
        except:
            res = produce_exception()
        return {'res': res}

def create_public_tenant1():
    domain_url = 'domain.local'
    tenant = Client(schema_name='public',name='Public',domain_url='localhost')
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here! on a local server you'll want to use localhost here
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()


def create_real_tenant(t_name):
    if not Client.objects.filter(schema_name='public'):
        create_public_tenant1()
    if Client.objects.filter(schema_name=t_name):
        return 'Customer '+t_name+' Already exists'
    domain_url = t_name + '.localhost'
    tenant = Client(schema_name=t_name, name=t_name, domain_url=domain_url)
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here!
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    return { 'done': True, 'url': domain_url }


class Create(TemplateView):
    template_name = "new_customer.html"

    def get_context_data(self, **kwargs):
        res = 'Unknown status'
        tenant_name = 'Untitiled'
        context = {}
        try:
            tenant_name = self.request.GET['name']
            res = create_real_tenant(tenant_name)
            if type(res) is str:
                context = {'message': res, 'domain_url': tenant_name + '.localhost'}
            else:
                message = 'You have successfully created customer "' + tenant_name + '"'
                context = {'name': tenant_name, 'done': 1, 'domain_url': res['url'], 'message': message}
        except:
            res = produce_exception()
        return context


def get_customer_list():
    tenants_list = Client.objects.all().values('id', 'name', 'domain_url')
    tenants_list = list(tenants_list)
    return tenants_list

class Delete(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        res = 'Unknown status'
        customer_id = self.request.GET['id']
        context = {}
        try:
            customer = Client.objects.get(pk=customer_id)
            if customer.schema_name == 'public':
                context = {'message': 'Can not delete public schema', 'list': get_customer_list()}
            customer.delete()
            context = {'list': get_customer_list()}
        except:
            res = produce_exception()
            context = {'message': res, 'list': get_customer_list()}
        return context


class TenantView(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        context = {'list': get_customer_list()}
        return context