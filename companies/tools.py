from django.db import connection
from django_tenants.utils import get_tenant_model


def switch_tenant(tenant_schema):
    tenant_model = get_tenant_model()
    now_tenant = tenant_model.objects.get(schema_name=tenant_schema)
    connection.set_tenant(now_tenant)
