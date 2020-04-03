import sys
import traceback
from datetime import datetime
from datetime import timedelta
from main_app.settings import PROTOCOL, MAIN_URL


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            error_message += er + '\n'
    return error_message


def get_company_url(schema_name):
    url = PROTOCOL + '://' + schema_name + '.' + MAIN_URL
    return url


def set_obj_attrs(dict_key_values, py_obj):
    for prop in dict_key_values:
        py_obj. __setattr__(prop, dict_key_values[prop])


def add_interval(interval_type, inc, dt=None):
    inc = int(inc)
    if not dt:
        dt = datetime.now()
    if interval_type == 'years':
        dt = dt + timedelta(years=inc)
    if interval_type == 'months':
        dt = dt + timedelta(months=inc)
    if interval_type == 'days':
        dt = dt + timedelta(days=inc)
    if interval_type == 'hours':
        dt = dt + timedelta(hours=inc)
    if interval_type == 'minutes':
        dt = dt + timedelta(minutes=inc)
    if interval_type == 'seconds':
        dt = dt + timedelta(seconds=inc)
    return dt


def queryset_to_list_search(queryset,fields=None,to_str=None,related=None):
    list = []
    for obj in queryset:
        dict = obj_to_dict_search(obj,fields,to_str,related)
        if dict:
            list.append(dict)

    return list


def send_email_on_creation(email_data):
    subject = email_data['subject']
    post_info = email_data['post_info']
    audience = email_data['audience']
    template_data = email_data['template_data']
    template_name = email_data['template_name']
    token_required = email_data.get('token_required')
    thread_data = {
        'subject': subject,
        'audience': audience,
        'template_data': template_data,
        'template_name': template_name,
        'token_required': token_required,
        'post_info': post_info
    }
    EmailThread(thread_data).start()


def obj_to_dict_search(obj,fields=None,to_str=None,related=None):
    if fields:
        dict = model_to_dict(obj,fields)
        for field in fields:
            if field.find("__") != -1:
                val = getattr(obj, field.split("__")[0])
                if val:
                    val = getattr(val, field.split("__")[1])
                dict[field] = val
    else:
        dict = model_to_dict(obj)

    res_dict = {}
    for field_name, val in dict.items():
                #handled non url file fields (saved as binary string)
        if type(dict[field_name]) is str or type(dict[field_name]) is int:
            res_dict[field_name] = val
    return res_dict


def search_db(params, search_fields=None):
    results = None
    search_text = params['kw'].lower()
    search_models = params.get('search_models')

    for app_name in search_models:
        for model_name in search_models[app_name]:
            fields = search_apps[app_name][model_name]
            kwargs = {}
            q_objects = Q()
            for field in fields:
                q_objects |= Q(**{field+'__contains': params['kw']})
                kwargs.update({'{0}__{1}'.format(field, 'contains'): search_text})
            model_obj = apps.get_model(app_name, model_name)
            search_result = model_obj.objects.filter(q_objects).order_by('-pk')
            results = search_result
    return results

def queryset_to_list(queryset,fields=None,to_str=None,related=None):
    list = []
    for obj in queryset:
        dict = obj_to_dict(obj,fields,to_str,related)
        list.append(dict)

    return list