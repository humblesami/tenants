from django.db import utils
from django.http import Http404
from django.db import connection
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_public_schema_name, get_tenant_domain_model


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        connection.set_schema_to_public()
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        selected_schema_name = 'public'

        try:
            domain = get_tenant_domain_model().objects.select_related('tenant').get(domain=hostname_without_port)
            request.tenant = domain.tenant
            selected_schema_name = request.tenant.schema_name
            request.urlconf = settings.TENANT_URLCONF
        except utils.DatabaseError:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
            return
        except get_tenant_domain_model().DoesNotExist:
            if hostname_without_port in ("127.0.0.1", "localhost"):
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
                return
            else:
                raise Http404

        connection.set_tenant(request.tenant)
        ContentType.objects.clear_cache()

        ps = get_public_schema_name()
        # if hasattr(settings, 'PUBLIC_SCHEMA_URLCONF') and selected_schema_name == ps:
        if selected_schema_name == ps:
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
