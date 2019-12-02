from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_tenant_model


class TenantMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 200 and response.status_code != 302 and request.path != '/favicon.ico':
            error_content = response.content.decode("utf-8")
            return render(request, 'error.html', {'error': error_content, 'error_code': response.status_code})
        return response

    def process_request(self, request):
        connection.set_schema_to_public()
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        selected_schema_name = ''
        tenant_model = get_tenant_model()

        if hostname_without_port.startswith('login.'):
            selected_schema_name = 'public'
        elif hostname_without_port == settings.TENANT_DOMAIN:
            selected_schema_name = 'public'

        if selected_schema_name == 'public':
            tenant = tenant_model.objects.filter(schema_name='public').first()
            if tenant:
                request.tenant = tenant
                connection.set_tenant(request.tenant)
                ContentType.objects.clear_cache()
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
            return

        tenant = tenant_model.objects.filter(domain_url=hostname_without_port).first()
        if not tenant:
            res = {
                'error': 'Subdomain ' + hostname_without_port + ' does not exist',
                'status': 'Invalid Client'
            }
            return render(request, '404.html', res)

        request.tenant = tenant
        connection.set_tenant(request.tenant)
        ContentType.objects.clear_cache()