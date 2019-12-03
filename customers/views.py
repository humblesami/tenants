from django.db import transaction
from django.views.generic import TemplateView
from django_tenants.utils import get_tenant_model
from tenant_users.permissions.models import UserTenantPermissions

from users.models import TenantUser
from tenant_tutorial import ws_methods
from tenant_tutorial.settings import SERVER_PORT_STR

from tenant_users.tenants.tasks import provision_tenant
from tenant_users.tenants.utils import create_public_tenant


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
            with transaction.atomic():
                # public_owner = "owner@local"
                # create_public_tenant("abc.com", public_owner)
                # TenantUser.objects.create_superuser(email="sa@abc.com", password='123', is_active=True)
                # tenant_admin_email = "admin@" + tenant_name
                # TenantUser.objects.create_user(email=tenant_admin_email, password='123', is_active=True, is_staff=True)
                # provision_tenant(tenant_name, tenant_name, tenant_admin_email, is_staff=True)
                # TenantUser.objects.create_user(email=tenant_admin_email, password='123', is_active=True, is_staff=True)
                
                if not get_tenant_model().objects.filter(schema_name='public'):
                    public_owner = "owner@local"
                    create_public_tenant("abc.com", public_owner)
                    TenantUser.objects.create_superuser(email="sa@abc.com", password='123', is_active=True)
                if not get_tenant_model().objects.filter(name=tenant_name):
                    tenant_admin_email = "admin@" + tenant_name
                    TenantUser.objects.create_user(email=tenant_admin_email, password='123', is_active=True, is_staff=True)
                    pot = provision_tenant(tenant_name, tenant_name, tenant_admin_email, is_staff=True)
                    context['message'] = tenant_name + ' created successfully'
                else:
                    context['error'] = 'Already exists'
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
            self.request.user = TenantUser.objects.filter(pk=1)
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