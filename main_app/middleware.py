import re
from django.conf import settings
from django.db import connection
from django.shortcuts import render
from django.db import utils, transaction
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_tenant_model

from main_app.settings import LOGOUT_URL, LOGIN_URL, ROOT_URL


def create_public_tenant(tenant_model):
    try:
        with transaction.atomic():
            owner = User.objects.create(username='admin@public', is_superuser=True, is_staff=True, is_active=True)
            owner.set_password('123')
            owner.save()
            t_name = 'public'
            company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id)
            company.save()
            return company
    except:
        return 'Web could not be initialized'


class RequireLoginMiddleware(object):
    def __init__(self):
        self.urls = tuple([re.compile(url) for url in settings.LOGIN_REQUIRED_URLS])
        self.require_login_path = getattr(settings, 'LOGIN_URL', LOGIN_URL)

    def process_request(self, request):
        for url in self.urls:
            if url.match(request.path) and request.user.is_anonymous():
                return HttpResponseRedirect('%s?next=%s' % (self.require_login_path, request.path))


class TenantMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 301 and response.status_code != 200 and response.status_code != 302 and request.path != '/favicon.ico':
            error_content = response.content.decode("utf-8")
            return render(request, 'error.html', {'error': error_content, 'error_code': response.status_code})
        return response

    def process_request(self, request):
        connection.set_schema_to_public()
        schema_name = remove_www_and_dev(request.get_host().split(':')[0])
        if '.' in schema_name:
            schema_name = schema_name.split('.')[0]
            if schema_name == 'login':
                schema_name = 'public'
        else:
            schema_name = 'public'
        tenant_model = get_tenant_model()
        request.logout_url = LOGOUT_URL
        request.root_url = ROOT_URL
        request.login_url = LOGIN_URL
        try:
            tenant = tenant_model.objects.filter(name=schema_name)
            if tenant:
                tenant = tenant[0]
                request.tenant = tenant
                selected_schema_name = tenant.schema_name
            else:
                res = {
                    'error': 'Subdomain ' + schema_name + ' does not exist',
                    'status': 'Invalid Client'
                }
                if schema_name != settings.TENANT_DOMAIN:
                    return render(request, 'error.html', {'error': 'Not found', 'error_code': 404})
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