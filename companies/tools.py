from django.db import connection
from django.contrib.auth.models import User
from django_tenants.utils import get_tenant_model

from py_utils.helpers import LogUtils


def switch_tenant(tenant_schema):
    tenant_model = get_tenant_model()
    now_tenant = tenant_model.objects.get(schema_name=tenant_schema)
    connection.set_tenant(now_tenant)


def create_tenant_root_user(schema_name, email, password):
    try:
        switch_tenant(schema_name)
        new_user = User.objects.create(
            username=email, email=email, is_staff=True,
            is_active=True, is_superuser=True
        )
        new_user.set_password(password)
        new_user.save()
        switch_tenant('public')
    except:
        err = LogUtils.get_error_message()
        switch_tenant('public')
        a = 1
