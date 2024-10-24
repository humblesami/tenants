import base64
import threading
from urllib.parse import unquote

from django.apps import apps
from django.db.models import Q
from django.conf import settings
from django.db import connection
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from .py import LogUtils, RtcUtils


class EmailUtils:

    @classmethod
    def send_mail_data(cls, mail_data):
        html_message = render_to_string(mail_data['template_data'], mail_data['template_name'])
        cls.send_email_thread(mail_data['emails'], mail_data['subject'], html_message)

    @classmethod
    def send_email_thread(cls, receiver_emails, subject, html_message, sender_email="sami@gmail.com"):

        def sender_method():
            try:
                send_mail(
                    subject, "", recipient_list=receiver_emails,  from_email=sender_email,
                    fail_silently=False, html_message=html_message
                )
            except:
                LogUtils.log_error()

        thread = threading.Thread(target=sender_method)
        thread.start()


class DbUtils:

    @classmethod
    def search_db(cls, params, search_fields=None):
        results = None
        search_text = params['kw'].lower()
        search_models = params.get('search_models')
        param_search_apps = params.get('search_apps')
        if not param_search_apps:
            if hasattr(settings, 'SEARCH_APPS'):
                param_search_apps = settings.SEARCH_APPS
        search_apps = param_search_apps or {}

        for app_name in search_models:
            for model_name in search_models[app_name]:
                if not search_apps.get(app_name):
                    raise 'App '+ app_name+' not found in search_apps'
                fields = search_fields or search_apps[app_name][model_name]
                kwargs = {}
                q_objects = Q()
                for field in fields:
                    q_objects |= Q(**{field + '__contains': params['kw']})
                    kwargs.update({'{0}__{1}'.format(field, 'contains'): search_text})
                model_obj = apps.get_model(app_name, model_name)
                search_result = model_obj.objects.filter(q_objects).order_by('-pk')
                results = search_result
        return results

    @classmethod
    def execute_update(cls, query, params=None):
        cr = connection.cursor()
        if params:
            cr.execute(query, params)
        else:
            cr.execute(query)
        res = cr.rowcount
        return res

    @classmethod
    def execute_query(cls, query, params=None):
        cr = connection.cursor()
        if params:
            cr.execute(query, params)
        else:
            cr.execute(query)
        rows = cr.fetchall()
        return rows

    @classmethod
    def dict_fetch_all(cls, query, params=None):
        cr = connection.cursor()
        if params:
            cr.execute(query, params)
        else:
            cr.execute(query)
        desc = cr.description
        res = [row for row in cr.fetchall()]
        dict_list = [dict(zip([col[0].replace('.', '=>') for col in desc], row)) for row in res]
        return dict_list

    @classmethod
    def get_fields_for_tables(cls, tables):
        table_names = "','".join(tables)
        db_name = connection.settings_dict['NAME']
        query = "select concat(table_name,'.',column_name) from information_schema.columns"
        query += f" where table_schema='{db_name}' and table_name in ('{table_names}')"
        res = cls.execute_query(query)
        columns = []
        for item in res:
            columns.append(item[0])
        return columns

    @classmethod
    def filtered_list(cls, list_objects, params):
        try:
            search_kw = params.get('search_kw')
            show_fields = params.get('fields') or ''
            search_fields = params.get('search_fields')
            sort_by = params.get('sort_by')
            page_no = 0
            page_size = params.get('page_size')
            if page_size:
                page_size = int(page_size)
                page_no = params.get('page_no') or 1
                if page_no:
                    page_no = int(page_no)
            args = Q()
            if search_fields:
                args_dict = {}
                arr = search_fields.split(',')
                for item in arr:
                    args_dict[item+'__icontains'] = search_kw
                args.add(Q(**args_dict), Q.OR)
            list_data1 = list_objects.filter(args).distinct()
            pagination = {}
            if sort_by:
                sort_by = sort_by.split(',')
                list_data1 = list_data1.order_by(*sort_by)
            if page_size:
                page_no = page_no or 1
                if page_no < 1:
                    page_no = 1
                paginator = Paginator(list_data1, page_size)
                page_count = paginator.num_pages
                if page_no >= page_count:
                    page_no = page_count
                records_on_page = paginator.per_page
                if page_no == page_count:
                    records_on_page = paginator.count % paginator.per_page

                list_data1 = paginator.page(page_no)
                pagination = {
                    'num_pages': paginator.num_pages,
                    'count': paginator.count,
                    'page_number': page_no,
                    'per_page': paginator.per_page,
                    'records_on_page': records_on_page
                }
                list_data1 = list_data1.object_list
            if show_fields:
                show_fields = show_fields.split(',')
                list_data1 = list_data1.values(*show_fields)
            else:
                list_data1 = list_data1.values()
            list_data1 = cls.serialize_list(list_data1)
            return list_data1, pagination
        except:
            LogUtils.log_error()
            raise

    @classmethod
    def serialize_object(cls, item):
        dict_obj = {}
        for key in item:
            attr = item[key]
            dict_obj[key] = attr
        return dict_obj

    @classmethod
    def serialize_list(cls, data):
        res = []
        for item in data:
            res.append(cls.serialize_object(item))
        return res


class DjangoUtils:

    @classmethod
    def queryset_to_list(cls, queryset, fields=None, to_str=None, related=None):
        obj_list = []
        for obj in queryset:
            dict_obj = cls.obj_to_dict(obj, fields, to_str, related)
            obj_list.append(dict_obj)
        return obj_list

    @classmethod
    def obj_to_dict(cls, obj, fields=None, to_str=None, related=None):
        if fields:
            dict_obj = model_to_dict(obj, fields)
            for field in fields:
                if field.find("__") != -1:
                    val = getattr(obj, field.split("__")[0])
                    if val:
                        val = getattr(val, field.split("__")[1])
                    dict_obj[field] = val
        else:
            dict_obj = model_to_dict(obj)

        for field in dict_obj:
            # handled non url file fields (saved as binary string)
            if type(dict_obj[field]) is not str and type(dict_obj[field]) is not int:
                if dict_obj[field]:
                    if str(type(dict_obj[field])) in ["<class \'datetime.datetime\'>", "<class 'datetime.date'>"]:
                        dict_obj[field] = str(dict_obj[field])
                    elif str(type(dict_obj[field])) in ["<class \'django.db.models.fields.files.FieldFile\'>",
                                                    '<class \'django.db.models.fields.files.ImageFieldFile\'>']:
                        try:
                            file_url = dict_obj[field].url
                            if not file_url:
                                dict_obj[field] = str(dict_obj[field])
                            else:
                                dict_obj[field] = file_url
                        except:
                            if dict_obj[field].startswith('/media/data'):
                                dict_obj[field] = dict_obj[field][7:]
                                dict_obj[field] = unquote(dict_obj[field])
                else:
                    dict_obj[field] = None
        if to_str:
            for field in to_str:
                if dict_obj[field]:
                    dict_obj[field] = str(dict_obj[field])

        if related:
            for field in related:
                _to_str = related[field].get("to_str")
                _fields = related[field].get("fields")
                _related = related[field].get("related")
                rel_obj = getattr(obj, field)
                if rel_obj._queryset_class:
                    dict_obj[field] = cls.queryset_to_list(rel_obj.filter(), fields=_fields, to_str=_to_str, related=_related)

        return dict_obj


    @classmethod
    def get_user_name(cls, user):
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

    @classmethod
    def base64_str_to_file(cls, data, file_name):
        header, data = data.split(';base64,')
        decoded_file = base64.b64decode(data)
        return ContentFile(decoded_file, name=file_name)

    @classmethod
    def site_url(cls, request):
        host_url = f'{request.scheme}://{request.get_host()}'
        return host_url

    @classmethod
    def full_url(cls, request):
        return request.build_absolute_uri()

    @classmethod
    def emit_socket_event(cls, data):
        RtcUtils.emit_event(data, settings.SOCKET_SERVER_URL)

