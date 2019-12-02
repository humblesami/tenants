from django.db import transaction
from django.contrib.auth.models import User
from django.views.generic import TemplateView

from django_tenants.utils import get_tenant_model

from tenant_tutorial import ws_methods
from tenant_tutorial.settings import SERVER_PORT_STR, TENANT_DOMAIN


def create_tenant(t_name):
    res = 'Unknown issue'
    try:
        tenant_model = get_tenant_model()
        with transaction.atomic():
            if not tenant_model.objects.filter(schema_name=t_name):
                owner = User.objects.create(username='owner@'+t_name, is_superuser=True, is_staff=True, is_active=True)
                owner.set_password('123')
                owner.save()
                domain_url = t_name + '.' + TENANT_DOMAIN
                company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_url=domain_url)
                company.owner = owner
                company.save()
                company.users.add(owner)
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
            res = create_tenant(tenant_name)
            if res != 'done':
                context['error'] = res
            else:
                context['message'] = 'Successfully created '+tenant_name
        except:
            context['error'] = ws_methods.produce_exception()
        context['list'] = get_customer_list()
        context['port'] = SERVER_PORT_STR
        return context


def get_customer_list():
    tenants_list = get_tenant_model().objects.prefetch_related('domains').all()
    tenants_list = list(tenants_list.values('id', 'schema_name', 'domain_url'))
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