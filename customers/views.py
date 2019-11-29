import sys
import traceback

from django.contrib.auth.models import User
from django.db import transaction
from django.views.generic import TemplateView
from django_tenants.utils import get_tenant_model

from users.models import TenantUser
from customers.models import Client, Domain
from tenant_tutorial.settings import SERVER_PORT_STR

from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            errorMessage += er + '<br><br>'
    return errorMessage


class CreateCustomer(TemplateView):
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
            with transaction.atomic():
                super_user = "superuser@"+tenant_name
                if not get_tenant_model().objects.filter(schema_name = 'public'):
                    create_public_tenant("localhost:8000", "admin@localhost")
                    TenantUser.objects.create_superuser(email=super_user, password='123', is_active=True)

                if not get_tenant_model().objects.filter(name=tenant_name):
                    TenantUser.objects.create_user(email=super_user, password='123', is_active=True)
                    provision_tenant(tenant_name, tenant_name, super_user)
                    context['message'] = tenant_name + ' created successfully'
                else:
                    context['error'] = 'Already exists'
        except:
            context['error'] = produce_exception()
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
            self.request.user = TenantUser.objects.filter(pk=1)
            TenantModel.objects.get(pk = customer_id).delete_tenant()
            context = {'list': get_customer_list()}
        except:
            res = produce_exception()
            context = {'message': res, 'list': get_customer_list()}
        context['port'] = SERVER_PORT_STR
        return context


class TenantView(TemplateView):
    template_name = "tenant_list.html"

    def get_context_data(self, **kwargs):
        context = {'list': get_customer_list()}
        context['port'] = SERVER_PORT_STR
        return context