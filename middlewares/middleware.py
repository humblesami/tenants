from django.db import utils
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_domain_model, remove_www_and_dev


class CustomTenantMiddleware(TenantMainMiddleware):
    def process_response(self, request, response):
        # return response
        if response.status_code == 404 and 'No tenant for hostname' in str(response.content):
            return HttpResponse('Not found')
        else:
            return response

    def process_request(self, request):
        connection.set_schema_to_public()
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        try:
            domain = get_tenant_domain_model().objects.select_related('tenant').get(domain=hostname_without_port)
            request.tenant = domain.tenant
            connection.set_tenant(request.tenant)
        except utils.DatabaseError:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
            return
        except get_tenant_domain_model().DoesNotExist:
            if hostname_without_port in ("127.0.0.1", "localhost") or 'local' in hostname_without_port:
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
                return
            else:
                raise


    # def process_request(self, request):
    #     connection.set_schema_to_public()
    #     # hostname = self.hostname_from_request(request)
    #     hostname = request.get_host()
    #     hostname = remove_www(hostname)
    #     sub_domain = hostname.split('.')[0]
    #
    #     try:
    #         # get_tenant must be implemented by extending this class.
    #         TenantModel = get_tenant_model()
    #         tenant = self.get_tenant(TenantModel, sub_domain, request)
    #         assert isinstance(tenant, TenantModel)
    #         request.tenant = tenant
    #         connection.set_tenant(request.tenant)
    #
    #     except (TenantModel.DoesNotExist, AssertionError):
    #         request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
    #         request.public_tenant = True
    #         return

        # if hasattr(settings, 'PUBLIC_SCHEMA_URLCONF') and request.tenant.schema_name == get_public_schema_name():
        #     request.urlconf = settings.PUBLIC_SCHEMA_URLCONF

        # if hasattr(settings, 'PUBLIC_SCHEMA_URLCONF'):
        #     request.urlconf = settings.PUBLIC_SCHEMA_URLCONF