from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType

from django_tenants.utils import get_tenant_model

from main_app import ws_methods
from main_app.settings import SERVER_PORT_STR, TENANT_DOMAIN
from tenant_only.models import TenantUser


class Create(TemplateView):
    
    template_name = "customers/tenant_list.html"

    def get_context_data(self, **kwargs):
        context = {}
        user = self.request.user
        try:
            tenant_name = self.request.POST.get('name')
            if not tenant_name:
                tenant_name = self.request.GET.get('name')
            if not tenant_name:
                context ['error'] = 'No name provided'
                return context
            res = create_tenant(tenant_name, self.request)
            if res != 'done':
                context['error'] = res
            else:
                context['message'] = 'Successfully created '+tenant_name
        except:
            context['error'] = ws_methods.produce_exception()
        context['list'] = get_customer_list(user)
        context['port'] = SERVER_PORT_STR
        context['user'] = user
        return context


class Delete(TemplateView):
    
    template_name = "customers/tenant_list.html"

    def get_context_data(self, **kwargs):
        res = 'Unknown status'
        customer_id = self.request.GET['id']
        context = {}
        user = self.request.user
        try:
            TenantModel = get_tenant_model()
            TenantModel.objects.get(pk = customer_id).delete_tenant(user)
            context = {'list': get_customer_list()}
        except:
            res = ws_methods.produce_exception()
            context = {'error': res, 'list': get_customer_list(user)}
        context['port'] = SERVER_PORT_STR
        context['user'] = user
        return context


class TenantView(TemplateView):

    template_name = "customers/tenant_list.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = {'list': get_customer_list(user)}
        context['port'] = SERVER_PORT_STR
        context['user'] = user
        return context


def get_my_tenants(user):
    user_id = user.id
    tenants_list = []
    if user_id:
        tenants_list = get_tenant_model().objects.filter(users__in=[user_id])
        tenants_list = tenants_list.prefetch_related('domains').all()
        tenants_list = list(tenants_list.values('id', 'schema_name', 'domain_url'))
        tenants_list = list(tenants_list)
    return tenants_list


def get_customer_list(user):
    tenants_list = get_tenant_model().objects.prefetch_related('domains').all()
    tenants_list = list(tenants_list.values('id', 'schema_name', 'domain_url'))
    tenants_list = list(tenants_list)
    my_tenants = get_my_tenants(user)
    return {'all': tenants_list, 'mine': my_tenants, 'my_count': len(my_tenants)}


def create_tenant(t_name, request):
    res = 'Unknown issue'
    try:
        tenant_model = get_tenant_model()
        with transaction.atomic():
            if not tenant_model.objects.filter(schema_name=t_name):
                # create public user
                owner = User.objects.create(username='admin@'+t_name, is_active=True)
                owner.set_password('123')
                owner.save()

                # create tenant
                domain_url = t_name + '.' + TENANT_DOMAIN
                company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_url=domain_url)
                company.save()
                company.users.add(owner)

                # select created tenant
                request.tenant = company
                connection.set_tenant(request.tenant)
                ContentType.objects.clear_cache()

                # create tenant user
                owner = TenantUser.objects.create(username='admin@' + t_name, is_superuser=True, is_staff=True,
                                                  is_active=True, is_schema_owner=True, password='123')
                owner.set_password('123')
                owner.save()

                # set tenant back to public
                connection.set_schema_to_public()
                ContentType.objects.clear_cache()

                res = 'done'
            else:
                res = 'Client with id' + t_name + ' already exists'
    except:
        res = ws_methods.produce_exception()
    return res

