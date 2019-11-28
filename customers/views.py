import sys
import traceback
from customers.models import Client, Domain
from django.views.generic import TemplateView


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
    tenant = Client(schema_name='public',name='Public')
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here! on a local server you'll want to use localhost here
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()


def create_real_tenant(t_name):
    if not Client.objects.filter(schema_name='public'):
        create_public_tenant()
    if Client.objects.filter(schema_name=t_name):
        return 'Customer '+t_name+' Already exists'
    domain_url = t_name + '.localhost'
    tenant = Client(schema_name=t_name, name=t_name)
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


class TenantView(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        tenants_list = Client.objects.all().values('id', 'name')
        tenants_list = list(tenants_list)
        context = {'list': tenants_list}
        return context