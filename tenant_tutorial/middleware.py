from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.db import utils, transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_tenant_model


def create_public_tenant(tenant_model):
    try:
        with transaction.atomic():
            owner = User.objects.create(username='admin@public', is_superuser=True, is_staff=True, is_active=True)
            owner.set_password('123')
            owner.save()
            t_name = 'public'
            domain_url = settings.TENANT_DOMAIN
            company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_url=domain_url)
            company.save()
            return company
    except:
        return 'Web could not be initialized'


class TenantMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 200 and response.status_code != 302 and request.path != '/favicon.ico':
            error_content = response.content.decode("utf-8")
            return render(request, 'error.html', {'error': error_content, 'error_code': response.status_code})
        return response

    def process_request(self, request):
        connection.set_schema_to_public()
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        selected_schema_name = 'public'
        tenant_model = get_tenant_model()
        try:
            if hostname_without_port.startswith('login.'):
                hostname_without_port = hostname_without_port.replace('login.', '')

            tenant = tenant_model.objects.filter(domain_url=hostname_without_port)
            if tenant:
                tenant = tenant[0]
                request.tenant = tenant
                selected_schema_name = tenant.schema_name
            else:
                res = {
                    'error': 'Subdomain ' + hostname_without_port + ' does not exist',
                    'status': 'Invalid Client'
                }
                if hostname_without_port != settings.TENANT_DOMAIN:
                    return render(request, '404.html', res)
                tenant = tenant_model.objects.filter(schema_name='public')
                if not tenant:
                    tenant = create_public_tenant(tenant_model)
                    if type(tenant) is not str:
                        request.tenant = tenant
                        selected_schema_name = tenant.schema_name
                    else:
                        return render(request, '404.html', res)
                else:
                    tenant = tenant[0]
                    request.tenant = tenant
                    selected_schema_name = tenant.schema_name
        except utils.DatabaseError:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
            return

        connection.set_tenant(request.tenant)
        ContentType.objects.clear_cache()

        if selected_schema_name == 'public':
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF