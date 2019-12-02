from django.conf import settings
from django.db import connection, utils
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
        request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        if hostname_without_port.startswith('login.'):
            hostname_without_port = hostname_without_port.replace('login.')

        tenant = get_tenant_model().objects.filter(domain_url=hostname_without_port)
        if tenant:
            request.tenant = tenant[0]
            request.urlconf = settings.ROOT_URLCONF
        else:
            if hostname_without_port == settings.TENANT_DOMAIN:
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
                return

        connection.set_tenant(request.tenant)
        ContentType.objects.clear_cache()

        if hostname_without_port == settings.TENANT_DOMAIN:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF