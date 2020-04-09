import os
import json
import urllib
import base64

import pytz
import requests
import threading
from random import randint
from urllib.parse import urlsplit
from urllib.request import urlopen
from urllib.parse import quote, unquote
from PIL import ImageFont, Image, ImageDraw
from rest_framework.authtoken.models import Token

from django.apps import apps
from django.db.models import Q
from django.db import connection
from django.contrib.auth import login
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile

from mainapp.settings import SOCKET_SERVER_URL
from emailthread.models import EmailThread


import sys
import traceback
from datetime import datetime
from datetime import timedelta
from mainapp.settings import PROTOCOL, server_domain, SERVER_PORT_STR


def get_company_url(schema_name):
    url = PROTOCOL + '://' + schema_name + '.' + server_domain + SERVER_PORT_STR
    return url


def dt_now():
    dt = datetime.now()
    dt = dt.replace(tzinfo=pytz.utc)
    return dt


def diff_seconds(dt1, dt2=None):
    if not dt2:
        dt2 = dt_now()
    diff = dt2 - dt1
    return diff.seconds


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


def now_str():
    now = str(datetime.now())
    now = now.replace(' ','-')
    now = now.replace(':', '-')
    now = now.replace('.', '-')
    return now


def get_user_name(user):
    name = False
    if user.first_name:
        name = user.first_name
        if user.last_name:
            name += ' ' + user.last_name
    elif user.last_name:
        name += user.last_name
    else:
        name = user.username
    return name


def send_email(subject, html_message, recipients):
    if not subject:
        return 'No Subject to mail'
    if not html_message:
        return 'No message to send mail',
    send_mail(subject, "", "sami@gmai.com",recipients
              , fail_silently=False,
              html_message=html_message)


socket_server = {
    'url': SOCKET_SERVER_URL,
    'connected': False
}


def execute_update(query):
    cr = connection.cursor()
    res = cr.execute(query)
    return res


def stringify_fields(dict_object):
    if dict_object.get('updated_at'):
        dict_object['updated_at'] = str(dict_object['updated_at'])
    if dict_object.get('created_at'):
        dict_object['created_at'] = str(dict_object['created_at'])
    if dict_object.get('updated_by'):
        dict_object['updated_by'] = str(dict_object['updated_by'])
    if dict_object.get('created_by'):
        dict_object['created_by'] = str(dict_object['created_by'])


def execute_read(query):
    cr = connection.cursor()
    cr.execute(query)
    res = cr.dictfetchall()
    return res


def set_obj_attrs(dict_key_values, py_obj):
    for prop in dict_key_values:
        py_obj. __setattr__(prop, dict_key_values[prop])


def base64_str_to_file(data, file_name):
    if 'data:' in data and ';base64,' in data:
        header, data = data.split(';base64,')
    try:
        decoded_file = base64.b64decode(data)
    except:
        raise ValueError('Invalid binary')

    return ContentFile(decoded_file, name=file_name)


def choices_to_list(choice_list):
    lst = []
    for choice in choice_list:
        lst.append({'id': choice[0], 'name': str(choice[1])})
    return lst


def http(req_url, headers=None):
    try:
        res = ''
        if headers:
            res = requests.get(req_url, headers=headers)
        else:
            res = requests.get(req_url)
        res = res.content
    except:
        res = 'Request failed because ' + str(sys.exc_info())
        print(res)
    return res


def http_request(req_url):
    try:
        host_url = "{0.scheme}://{0.netloc}/".format(urlsplit(req_url))
        try:
            r = requests.get(host_url)
            r.raise_for_status() # Raises a HTTPError if the status is 4xx, 5xxx
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            res = host_url + " is not available"
        except requests.exceptions.HTTPError:
            res = 'httperror'
        else:
            res = requests.get(req_url)
            res = res._content.decode("utf-8")
        return res
    except:
        res = 'socket request failed because ' + str(sys.exc_info())
        print(res)
    return res


def emit_event(data, req_url=None):
    url = ''
    try:
        if not data:
            data = []
        data = json.dumps(data)
        data = quote(data)
        req_url = '/odoo_event'
        try:
            url = socket_server['url'] + req_url
        except:
            return 'Error socket server url'
        url += '?data=' + data
    except:
        return 'Error in given data '+ str(data)
    try:
        return http_request(url)
    except:
        return 'Error in url ' + url


def obj_to_dict(obj,fields=None,to_str=None,related=None):
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

    for field in dict:
        #handled non url file fields (saved as binary string)
        if type(dict[field]) is not str  and type(dict[field]) is not int:
            if dict[field]:
                if str(type(dict[field])) in ["<class \'datetime.datetime\'>", "<class 'datetime.date'>"]:
                    dict[field] = str(dict[field])
                elif str(type(dict[field])) in ["<class \'django.db.models.fields.files.FieldFile\'>",'<class \'django.db.models.fields.files.ImageFieldFile\'>']:
                    try:
                        file_url = dict[field].url
                        if not file_url:
                            dict[field] = str(dict[field])
                        else:
                            dict[field] = file_url
                    except:
                        if dict[field].startswith('/media/data'):
                            dict[field] = dict[field][7:]
                            dict[field] = unquote(dict[field])
            else:
                dict[field] = None
    if to_str:
        for field in to_str:
            if dict[field]:
                dict[field] = str(dict[field])

    if related:
        for field in related:
            _to_str = related[field].get("to_str")
            _fields = related[field].get("fields")
            _related = related[field].get("related")
            rel_obj = getattr(obj, field)
            if rel_obj._queryset_class:
                dict[field] = queryset_to_list(rel_obj.filter(),fields=_fields,to_str=_to_str,related=_related)

    return dict


def queryset_to_list(queryset,fields=None,to_str=None,related=None):
    list = []
    for obj in queryset:
        dict = obj_to_dict(obj,fields,to_str,related)
        list.append(dict)

    return list


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


def queryset_to_list_search(queryset,fields=None,to_str=None,related=None):
    list = []
    for obj in queryset:
        dict = obj_to_dict_search(obj,fields,to_str,related)
        if dict:
            list.append(dict)

    return list


def get_model(app_name, model_name):
    try:
        model = apps.get_model(app_name, model_name)
        return model
    except:
        return 'model not found'


def check_auth_token(request,values):
    if request.user and not request.user.is_anonymous:
        return request.user.id
    if not values['auth_token']:
        return False
    token = Token.objects.filter(key=values['auth_token'])
    if not token.exists():
        return False
    user = token[0].user
    login(request, user)

    return user.id


def replace_key_in_dict(values, old_key, new_key):
    for obj in values:
        obj[new_key] = obj.pop(old_key)

    return values


def threaded_operation(operation, args):
    obj = threading.Thread(target=operation, args=args)
    obj.start()


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


def validate_token(token, kw=None, do_not_expire=None):
    post_user_token = get_model('restoken', 'PostUserToken')
    if type(post_user_token) is str:
        return 'Model not found'
    user_token = post_user_token.validate_token(token, do_not_expire)
    if not user_token:
        return 'You are not authorized'
    if 'id' in kw.keys():
        post_res_id = kw['id']
        if int(post_res_id) != user_token.post_info.res_id:
            return 'Token is not valid'
    return user_token.user


def get_user_by_token(request, kw=None, do_not_expire=None):
    token = ''
    user = {}
    if request.GET:
        token = request.GET['token']
    if not token:
        if request.POST:
            token = request.POST['token']
            if token:
                user = validate_token(token, request.POST, do_not_expire=do_not_expire)
                if type(user) is str:
                    return user
    if not token and kw and kw.get('token'):
        token = kw['token']
        user = validate_token(token, kw, do_not_expire=do_not_expire)
        if type(user) is str:
            return user
    if not user:
        user = request.user
    if user and user.id:
        return user
    else:
        return 'You are not authorized'


def get_user_info(users):
    users_info = []
    for user in users:
        user_info = {}
        user_info['id'] = user_info['uid'] = user.id
        user_info['name'] = user.fullname()
        user_info['photo'] = user_info['image'] = user.image.url
        user_info['email'] = user.email
        user_info['company'] = user.company
        user_info['mobile_phone'] = user.mobile_phone
        user_info['department'] = user.department
        groups = list(user.groups.all())
        group_name = []
        if len(groups) > 0:
            for grp in groups:
                group_name.append(grp.name.lower())
        user_info['group'] = group_name
        user_committees =  obj_to_dict(user,
            fields = [],
            related={
                'committees': {'fields': ['id', 'name']}
            }
        )
        committees = []
        for com in user_committees['committees']:
            committees.append(com)
        user_info['committees'] = committees
        users_info.append(user_info)
    return users_info


def get_error_message():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\site-packages' in er:
            errorMessage += " " + er
    return errorMessage


def has_permission(res):
    user_permission = False
    model = res['model']
    permissions = res['permissions']
    user = res['user']
    groups = user.groups.all()
    for group in groups:
        for permission_type in permissions:
            permission = group.permissions.filter(codename=permission_type+'_'+model)
            if permission:
                user_permission = True
    return user_permission


def duplicate_file(a, file_ptr, file_type):
    a.name = file_ptr.name
    a.html = file_ptr.html
    a.content = file_ptr.content
    a.pdf_doc = file_ptr.pdf_doc
    a.file_type = file_ptr.file_type
    a.attachment = file_ptr.attachment

    a.file_name = file_ptr.file_name

    a.extention = file_ptr.extention
    a.access_token = file_ptr.access_token
    a.file_type = file_type
    a.pending_tasks = 0
    return a


def delete_all_temp_files(request, user_id):
    file_model = get_model('documents', 'File')
    method_to_call =  getattr(file_model, 'delete_all_tem_files')
    params = {'user_id': user_id}
    method_to_call(request, params)
    return 'done'


search_apps = {

}


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


def generate_default_image(name):
    curr_dir = os.path.dirname(__file__)
    directory = curr_dir.replace('model_files', 'static')
    if not os.path.exists(directory):
        os.makedirs(directory)
    txt = name
    txt = ''.join([x[0].upper() for x in txt.split(' ')])
    font_directory = curr_dir.replace('mainapp', 'static/assets/fonts')
    font = ImageFont.truetype(font_directory + "/roboto-v19-latin-regular.ttf", 48)
    img = Image.new('RGB', (100, 100), (randint(0, 255), randint(0, 255), randint(0, 255)))   # "L": (8-bit pixels, black and white)
    font = ImageFont.truetype(font_directory + "/roboto-v19-latin-regular.ttf", 48)
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(txt, font=font)
    h += int(h*0.21)
    draw.text(((100-w)/2, (100-h)/2), text=txt, fill='white', font=font)
    pic_name = "/pic" + str(randint(1, 9999999)) + ".png"
    img_path = directory.replace('mainapp', 'media/profile') + pic_name
    img.save(img_path)
    return 'profile' + pic_name


def bytes_to_json(my_bytes_value):
    my_json = {'error': 'Invalid bytes value to get json'}
    try:
        my_json = my_bytes_value.decode('utf8').replace("'", '"')
        my_json = json.loads(my_json)
    except:
        pass
    return my_json


def download_image(file):
    img_temp = NamedTemporaryFile(delete=True)
    try:
        if file['source'] == 'Google':
            headers = {'Authorization':'Bearer '+file['access_token']}
            request = urllib.request.Request(file['url'], headers=headers)
            img_temp.write(urlopen(request).read())
        else:
            img_temp.write(urlopen(file['url']).read())
        img_temp.flush()
        return img_temp
    except urllib.error.HTTPError as e:
        return str(e.code) + e.reason


def produce_exception(msg=None):
    error_message = ''
    if not msg:
        eg = traceback.format_exception(*sys.exc_info())
        cnt = 0
        for er in eg:
            cnt += 1
            if not 'lib/python' in er and not 'lib\\' in er:
                error_message += " " + er
    else:
        error_message = msg
    return error_message
    # try:
    #     dir = os.path.dirname(os.path.realpath(__file__))
    #     ar = dir.split('/')
    #     ar = ar[:-1]
    #     dir = ('/').join(ar)
    #     with open(dir+'/error_log.txt', "a+") as f:
    #         f.write(error_message + '\n')
    # except:
    #     try:
    #         dir = os.path.dirname(os.path.realpath(__file__))
    #         ar = dir.split('\\')
    #         ar = ar[:-1]
    #         dir = ('\\').join(ar)
    #         with open(dir + '\\error_log.txt', "a+") as f:
    #             f.write(error_message + '\n')
    #     except:
    #         eg = traceback.format_exception(*sys.exc_info())
    #         error_message = ''
    #         cnt = 0
    #         for er in eg:
    #             cnt += 1
    #             if not 'lib/python' in er:
    #                 error_message += " " + er
    #         return error_message
