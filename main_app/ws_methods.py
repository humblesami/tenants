import sys
import traceback

from main_app.settings import TENANT_DOMAIN, ROOT_URL


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            error_message += er + '<br><br>'
    return error_message


def get_company_url(schema_name):
    if schema_name == 'public':
        url = ROOT_URL
    else:
        url = ROOT_URL.replace(TENANT_DOMAIN, schema_name + '.' + TENANT_DOMAIN, 1)
    return url