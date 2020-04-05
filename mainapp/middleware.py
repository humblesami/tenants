import json
import sys
import traceback
from django.db import connection
from django.shortcuts import render
from django.db import utils, transaction
from django.contrib.auth.models import User

from django.http import JsonResponse, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_tenant_model

from mainapp.settings import PUBLIC_SCHEMA_URLCONF, PROTOCOL, server_domain, SERVER_PORT_STR, MAIN_URL, LOGIN_URL


def create_public_tenant(tenant_model):
    try:
        with transaction.atomic():
            owner = User.objects.create(username='admin@public', is_superuser=True, is_staff=True, is_active=True)
            owner.set_password('123')
            owner.save()
            t_name = 'public'
            domain_url = server_domain
            company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_url=domain_url)
            company.save()
            return company
    except:
        return 'Web could not be initialized'


class TenantMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.is_ajax():
            response = response.content
            response = response.decode("utf-8")
            response = produce_result_ajax(response)
            return HttpResponse(response)
        elif response.status_code and response.status_code != 301 and response.status_code != 200 and response.status_code != 302 and request.path != '/favicon.ico':
            error_content = response.content.decode("utf-8")
            if not error_content:
                error_content = 'Error '+ str(response.status_code)
            return render(request, 'error.html', {'error': error_content, 'error_code': response.status_code})
        return response

    # def process_exception(self, request, exception):
    #     res = produce_exception()
    #     # res = HttpResponse(res)
    #     return render(request, 'error.html', {'error': res})

    def process_request(self, request):
        try:
            connection.set_schema_to_public()
            hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
            selected_schema_name = 'public'
            tenant_model = get_tenant_model()
            request.main_url = MAIN_URL
            request.login_url = LOGIN_URL
            request.protocol = PROTOCOL
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
                not_found = {'error': 'This subdomain does not exist => '+hostname_without_port, 'error_code': 404}
                if hostname_without_port != server_domain:
                    return render(request, 'error.html', not_found)
                tenant = tenant_model.objects.filter(schema_name='public')
                if not tenant:
                    tenant = create_public_tenant(tenant_model)
                    if type(tenant) is not str:
                        request.tenant = tenant
                        selected_schema_name = tenant.schema_name
                    else:
                        return render(request, 'error.html', not_found)
                else:
                    tenant = tenant[0]
                    request.tenant = tenant
                    selected_schema_name = tenant.schema_name
                    request.home_url = PROTOCOL + "//" + selected_schema_name + '.' + server_domain + SERVER_PORT_STR
        except utils.DatabaseError:
            request.urlconf = PUBLIC_SCHEMA_URLCONF
            return

        connection.set_tenant(request.tenant, False)
        ContentType.objects.clear_cache()
        if selected_schema_name == 'public':
            request.urlconf = PUBLIC_SCHEMA_URLCONF


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            error_message += " " + er
    return error_message


def produce_result_ajax(res, args=None):
    valid_res = False
    try:
        temp = json.loads(res)
        if temp.get('error') or temp.get('data'):
            valid_res = True
    except:
        pass
    if valid_res:
        return res
    if isinstance(res, dict):
        if 'error' not in res:
            if 'data' in res:
                res['error'] = ''
            else:
                res = {'data': res, 'error': ''}
        else:
            # Return ERROR data as it is
            pass
    elif type(res) == str:
        if res == 'done':
            res = {'error': '', 'data': 'done'}
        else:
            res = {'error': res}
    elif isinstance(res, list):
        res = {'error': '', 'data': res}
    else:
        if args:
            args = ' in ' + args['app'] + '.' + args['model'] + '.' + args['method']
        else:
            args = ''
        res = {'error': ' Invalid result type' + args}
    json.dumps(res)
    return res


def produce_result(res, args=None):
    if isinstance(res, dict):
        if 'error' not in res:
            if 'data' in res:
                res['error'] = ''
            else:
                res = {'data': res, 'error': ''}
        else:
            # Return ERROR data as it is
            pass
    elif type(res) == str:
        if res == 'done':
            res = {'error': '', 'data': 'done'}
        else:
            res = {'error': res}
    elif isinstance(res, list):
        res = {'error': '', 'data': res}
    else:
        if args:
            args = ' in ' + args['app'] + '.' + args['model'] + '.' + args['method']
        else:
            args = ''
        res = {'error': ' Invalid result type' + args}
    return JsonResponse(res)