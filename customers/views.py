from django.contrib.auth.models import User
from django.db import transaction
from django.views.generic import TemplateView
from django_tenants.utils import get_tenant_model
from tenant_tutorial import ws_methods
from tenant_tutorial.settings import SERVER_PORT_STR


def create_public_tenant(TenantModel):
    User.objects.create(password='123', username='admin@public', is_superuser=True, is_verfied=True)
    TenantModel.objects.create(schema='public', name='Default')


def create_tenant(t_name):
    res = 'Unknown issue'
    try:
        TenantModel = get_tenant_model()
        with transaction.atomic():
            if not TenantModel.objects.get(schema='public'):
                create_public_tenant()
            if not TenantModel.objects.get(schema=t_name):
                user = User.objects.create(password='123', username='owner@'+t_name, is_superuser=True, is_verfied=True)
                company = TenantModel.objects.create(schema=t_name, name=t_name)
                company.owner = user
                company.users.add(user)
                res = 'done'
            else:
                res = 'Client with id' + t_name + ' already exists'
    except:
        res = ws_methods.produce_exception()
    return res


class Create(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        context = {}
        try:
            tenant_name = self.request.POST.get('name')
            if not tenant_name:
                tenant_name = self.request.GET.get('name')
            if not tenant_name:
                context ['error'] = 'No name provided'
                return context
            create_tenant(tenant_name)
        except:
            context['error'] = ws_methods.produce_exception()
        context['list'] = get_customer_list()
        context['port'] = SERVER_PORT_STR
        return context

def get_customer_list():
    tenants_list = get_tenant_model().objects.prefetch_related('domains').all()
    tenants_list = list(tenants_list.values('id', 'name', 'domains__domain'))
    tenants_list = list(tenants_list)
    return tenants_list

class Delete(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        res = 'Unknown status'
        customer_id = self.request.GET['id']
        context = {}
        try:
            TenantModel = get_tenant_model()
            TenantModel.objects.get(pk = customer_id).delete_tenant()
            context = {'list': get_customer_list()}
        except:
            res = ws_methods.produce_exception()
            context = {'error': res, 'list': get_customer_list()}
        context['port'] = SERVER_PORT_STR
        return context


class TenantView(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        context = {'list': get_customer_list()}
        context['port'] = SERVER_PORT_STR
        return context