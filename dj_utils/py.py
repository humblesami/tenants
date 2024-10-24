import sys
import json
import uuid
import pytz
import urllib
import asyncio
import requests
import threading
import traceback
import httpagentparser
from pathlib import Path
from os.path import dirname
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from datetime import datetime, timezone
from dateutil import parser as dt_parser
from dateutil.relativedelta import relativedelta


class RtcUtils:

    @classmethod
    def emit_event(cls, data, socket_server_url='', req_url=None):
        if not data:
            data = []
        data = json.dumps(data)
        data = quote(data)
        req_url = req_url or '/odoo_event'
        url = socket_server_url + req_url + '?data=' + data
        return HttpUtils.http_get(url)


class DateUtils:

    @classmethod
    def now_str(cls):
        now = str(datetime.now())
        now = now[:-7]
        return now

    @classmethod
    def diff_seconds(cls, dt1, dt2=None):
        if not dt2:
            dt2 = datetime.now()
        diff = dt2 - dt1
        return diff.seconds

    @classmethod
    def add_interval(cls, interval_type, inc, dt=None):
        inc = int(inc)
        if not dt:
            dt = datetime.now()
        elif type(dt) == str:
            dt = dt_parser.parse(dt)
        if interval_type == 'y':
            dt = dt + relativedelta(years=inc)
        if interval_type == 'mm':
            dt = dt + relativedelta(months=inc)
        if interval_type == 'w':
            dt = dt + relativedelta(weeks=inc)
        if interval_type == 'd':
            dt = dt + relativedelta(days=inc)
        if interval_type == 'h':
            dt = dt + relativedelta(hours=inc)
        if interval_type == 'm':
            dt = dt + relativedelta(minutes=inc)
        if interval_type == 's':
            dt = dt + relativedelta(seconds=inc)
        return dt

    @classmethod
    def time_difference(cls, start_time, end_time=None):
        if not end_time:
            end_time = datetime.now()
        start_time = start_time.replace(tzinfo=pytz.utc)
        end_time = end_time.replace(tzinfo=pytz.utc)
        diff = relativedelta(end_time, start_time)
        return diff

    @classmethod
    def string_format(cls, style='', dt=None):
        if not style:
            style = '%Y-%m-%d %I:%M:%S %p'
        if not dt:
            dt = datetime.now()
        if style == '14':
            style = '%Y%m%d%H%M%S'
        res = dt.strftime(style)
        return res

    @classmethod
    def time_to_utc(cls, dt):
        # dst_str = str(dt)
        # dst_str = '2021-09-21T09:29:21Z'
        dt_str = str(dt)
        dt_str = dt_str.replace(' ', 'T')
        if '.' in dt_str:
            dt_str = dt_str[:19] + 'Z'
        else:
            dt_str = dt_str.replace('+00:00', 'Z')
        return dt_str

    @classmethod
    def get_month_year(cls, dt):
        year = str(dt.year)
        month = dt.month
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        return year, month

    @classmethod
    def get_timestamp(cls, dt=None):
        if not dt:
            dt = datetime.now()
        elif type(dt) == str:
            dt = dt_parser.parse(dt)
        timestamp = round(dt.timestamp())
        return timestamp


class LogUtils:

    @classmethod
    def get_error_message(cls):
        eg = traceback.format_exception(*sys.exc_info())
        error_message = ''
        cnt = 0
        for er in eg:
            cnt += 1
            if not 'lib/python' in er and not 'lib\site-packages' in er:
                error_message += " " + er
        if not error_message:
            error_message = 'empty error'
        return error_message

    @classmethod
    def get_error_json(cls):
        eg = traceback.format_exception(*sys.exc_info())
        user = eg[len(eg) - 1]
        dev = cls.get_error_message()
        return {'user': user, 'dev': dev, 'error': dev, 'message': dev}

    @classmethod
    def log_error(cls, prefix=''):
        dir_path = dirname(__file__)
        dir_path = dirname(dir_path)
        file_name = dir_path + '/logs/errors.log'
        content = prefix + cls.get_error_message()
        cls.write_file(content, file_name, 1)

    @classmethod
    def write_file(cls, content='Nothing', file_name='', path_given=0):
        if not path_given:
            dir_path = dirname(dirname(__file__))
            if not file_name:
                file_name = dir_path + '/logs/errors.log'
            else:
                file_name = dir_path + '/logs/' + file_name
        f = open(file_name, "a")
        time_now = str(datetime.now())
        content = str(content)
        content = '\n' + content + '\n' + time_now + '\n'
        f.write(content)
        f.close()

    @classmethod
    def note_error(cls, content='', append=0):
        error_message = content
        if append:
            error_message = error_message + '\n' + cls.get_error_message()
        else:
            error_message = cls.get_error_message()
        cls.write_file(error_message)

    @classmethod
    def note_error_middleware(cls, content='', append=0):
        error_message = content
        if append:
            error_message = error_message + '\n' + cls.get_error_message()
        else:
            error_message = cls.get_error_message()
        cls.write_file(error_message, 'middleware.log')

    @classmethod
    def prepend(cls, file_path, txt, take_lines=20):
        dt_now = str(datetime.now(tz=timezone.utc))[:19]
        fle = Path(file_path)
        fle.touch(exist_ok=True)
        with open(file_path, 'r') as my_file:
            ii = 0
            prev_content = ''
            while ii < take_lines:
                line = next(my_file)
                if line:
                    prev_content += '\n' + line.strip()
                ii += 1
        with open(file_path, 'w') as my_file:
            new_content = dt_now + '\t' + txt + prev_content
            my_file.write(new_content)


class Async:

    @classmethod
    def run_in_background(cls, bg_fun):
        def wrapped(*args):
            looper = None
            try:
                looper = asyncio.get_event_loop()
            except RuntimeError as ex:
                if "There is no current event loop in thread" in str(ex):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    looper = asyncio.get_event_loop()
            return looper.run_in_executor(None, bg_fun, *args)

        return wrapped

    @classmethod
    async def async_functions_list_processor(cls, tasks_list):
        coroutines = []
        for task_to_do in tasks_list:
            coroutines.append(task_to_do)
        res = await asyncio.gather(*coroutines)
        return res

    @classmethod
    def threaded_operation(cls, operation, args):
        obj = threading.Thread(target=operation, args=args)
        obj.start()


class HttpUtils:

    @classmethod
    def get_location_from_ip(cls, server_url, ip, query_string):
        req_url = server_url + ip + query_string
        print(req_url)
        res = cls.http_get_json(req_url)
        return res

    @classmethod
    def get_browser(cls, agent):
        browser = httpagentparser.detect(agent)
        if not browser:
            browser = agent.split('/')[0]
        else:
            browser = browser['browser']['name']

        return browser

    @classmethod
    def get_client_ip(cls, req_meta):
        x_forwarded_for = req_meta.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = req_meta.get('REMOTE_ADDR')
        return ip

    @classmethod
    def http_get(cls, req_url, headers=None, timeout=5):
        res = requests.get(req_url, headers=headers, timeout=timeout)
        res = res._content.decode("utf-8")
        return res

    @classmethod
    def http_get_json(cls, req_url, headers=None, timeout=5):
        res = requests.get(req_url, headers=headers, timeout=timeout)
        res = res.json()
        return res

    @classmethod
    def get_str_from_post(cls, req_url, args=None):
        res = cls.post_data(req_url, args)
        res = res._content.decode("utf-8")
        return res

    @classmethod
    def get_json_from_post(cls, req_url, args=None):
        res = cls.post_data(req_url, args)
        return res.json()

    @classmethod
    def post_data(cls, req_url, args):
        headers = args.get('headers')  # 'application/json' if json_data else None
        json_data = args.get('json')
        timeout = args.get('timeout') or 6
        res = requests.post(req_url, timeout=timeout, data=json_data, headers=headers)
        return res


class PyUtils:

    @classmethod
    def download_image(cls, file):
        img_temp = NamedTemporaryFile(delete=True)
        try:
            if file['source'] == 'Google':
                headers = {'Authorization': 'Bearer ' + file['access_token']}
                request = urllib.request.Request(file['url'], headers=headers)
                img_temp.write(urlopen(request).read())
            else:
                img_temp.write(urlopen(file['url']).read())
            img_temp.flush()
            return img_temp
        except HTTPError as e:
            return str(e.code) + e.reason

    @classmethod
    def decode_bytes(cls, my_bytes_value):
        res = my_bytes_value.decode('utf8').replace("'", '"')
        return res

    @classmethod
    def set_obj_attrs(cls, dict_key_values, py_obj):
        for prop in dict_key_values:
            py_obj.__setattr__(prop, dict_key_values[prop])

    @classmethod
    def unique_id(cls):
        res = str(uuid.uuid4())
        return res

    @classmethod
    def get_file_extension(cls, file_name):
        arr = file_name.split('.')
        extension = arr[len(arr) - 1]
        return extension

    @classmethod
    def stringify_fields(cls, dict_object):
        if dict_object.get('updated_at'):
            dict_object['updated_at'] = str(dict_object['updated_at'])
        if dict_object.get('created_at'):
            dict_object['created_at'] = str(dict_object['created_at'])
        if dict_object.get('updated_by'):
            dict_object['updated_by'] = str(dict_object['updated_by'])
        if dict_object.get('created_by'):
            dict_object['created_by'] = str(dict_object['created_by'])


class JsonToObj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)


class JsonUtils:

    @classmethod
    def dict2obj(cls, dict_obj):
        res = json.loads(json.dumps(dict_obj), object_hook=JsonToObj)
        return res

    @classmethod
    def json_input(cls, kw, byte_data):
        if kw and len(kw.keys()):
            return kw
        if byte_data:
            data = byte_data.decode()
            if data:
                kw = json.loads(data)
        return kw
