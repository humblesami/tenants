from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.db import utils, transaction
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_tenant_model

from users.models import TenantUser
from .ws_methods import produce_exception
from tenant_users.tenants.utils import create_public_tenant


def create_custom_public_tenant():
    try:
        with transaction.atomic():
            tenant_admin_email = "admin@public"
            create_public_tenant(settings.TENANT_USERS_DOMAIN, tenant_admin_email)
            admin = TenantUser.objects.get(email=tenant_admin_email)
            admin.set_password('123')
            admin.save()
            return get_tenant_model().objects.get(schema_name='public')
    except:
        return produce_exception()


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

            schema_name = 'public'
            if hostname_without_port != settings.TENANT_USERS_DOMAIN:
                schema_name = hostname_without_port.split('.')[0]
            tenant = tenant_model.objects.filter(name=schema_name)
            if tenant:
                tenant = tenant[0]
                request.tenant = tenant
                selected_schema_name = tenant.schema_name
            else:
                schema_error = {
                    'error': 'Invalid client, Page Not found for schema '+selected_schema_name,
                    'hidden': '',
                    'error_code': 404
                }
                if hostname_without_port != settings.TENANT_USERS_DOMAIN:
                    return render(request, 'error.html', schema_error)
                tenant = tenant_model.objects.filter(schema_name='public')
                if not tenant:
                    tenant = create_custom_public_tenant()
                    if type(tenant) is not str:
                        request.tenant = tenant
                        selected_schema_name = tenant.schema_name
                    else:
                        schema_error['hidden'] = tenant
                        return render(request, 'error.html', schema_error)
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