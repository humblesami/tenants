import sys
import traceback
from django.db import connection
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin  # todo change
from django_tenants.utils import remove_www_and_dev, get_tenant_model


class TenantMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.is_ajax():
            response = response.content
            response = response.decode("utf-8")
            response = produce_result(response)
        elif response.status_code and response.status_code != 301 and response.status_code != 200 and response.status_code != 302 and request.path != '/favicon.ico':
            error_content = response.content.decode("utf-8")
            if not error_content:
                error_content = 'Error '+ str(response.status_code)
            return render(request, 'error.html', {'error': error_content, 'error_code': response.status_code})
        return response

    def process_exception(self, request, exception):
        res = produce_exception()
        res = HttpResponse(res)
        return res

    def process_request(self, request):
        selected_schema_name = 'public'
        try:
            connection.set_schema_to_public()
            hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
            tenant_model = get_tenant_model()
            url_parts = hostname_without_port.split('.')
            sub_domain = url_parts[0]
            if sub_domain == 'login':
                hostname_without_port = hostname_without_port.replace('login.', '')
            if hostname_without_port == settings.TENANT_DOMAIN:
                sub_domain = 'public'
            request.main_url = settings.MAIN_URL
            tenant = tenant_model.objects.filter(schema_name=sub_domain)
            if tenant:
                tenant = tenant[0]
                request.tenant = tenant
                selected_schema_name = tenant.schema_name
            else:
                res = {
                    'error': 'sub_domain ' + hostname_without_port + ' does not exist',
                    'status': 'Invalid Client',
                    'error_code': 404,
                }
                return render(request, 'error.html', res)
            if selected_schema_name == 'public':
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF

            connection.set_tenant(request.tenant)
            ContentType.objects.clear_cache()
        except:
            pass


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            error_message += " " + er
    return error_message


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