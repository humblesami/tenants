from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import json
import sys
import traceback
from django.apps import apps
from django.http import HttpResponse

from mainapp import ws_methods

public_methods = {
    'authsignup': {
        'AuthUser': {
            'login_user': 1,
            'reset_password': 1,
            'set_user_password': 1
        }
    },
    'meetings': {
        'Event': {
            'get_details': 1,
            'respond_invitation': 1
        },
    },
    'voting': {
        'VotingAnswer': {
            'submit_public': 1,
            'submit': 1,
        },
        'Voting': {
            'get_details': 1,
        }
    },
    'esign': {
        'SignatureDoc': {
            'get_signature': 1,
            'get_doc_data': 1,
            'get_detail': 1,
            'ws_get_detail': 1,
        },
        'Signature': {
            'save_signature': 1,
            'get_signature': 1,
            'load_signature': 1,
        }
    }
}


@csrf_exempt
def public(request):
    try:
        kw = request.POST
        res = 'Unknown'
        if not kw:
            kw = request.GET
        kw = json.loads(kw['input_data'])
        args = kw['args']
        try:
            res = public_methods[args['app']]
            res = res[args['model']]
            res = res[args['method']]
        except:
            res = 'Invalid method call'
            return produce_result(res, args)
        params = kw['params']
        model = apps.get_model(args['app'], args['model'])
        method_to_call = getattr(model, args['method'])
        res = method_to_call(request, params)
        return produce_result(res, args)
    except:
        return produce_exception_public()


@csrf_exempt
@api_view(["GET", "POST"])
def secure(request):
    try:
        kw = request.POST
        if not kw:
            kw = request.GET
        kw = json.loads(kw['input_data'])
        args = kw['args']
        params = kw['params']
        model = apps.get_model(args['app'], args['model'])
        method_to_call = getattr(model, args['method'])
        res = method_to_call(request, params)
        return produce_result(res, args)
    except:
        return produce_exception()


@login_required()
def search_session(request):
    try:
        if request.user.id != 1:
            return produce_result("unauthorized")
        results = search(request)
        return produce_result(results)
    except:
        return produce_exception()


@csrf_exempt
@api_view(["GET", "POST"])
def search_ws(request):
    try:
        results = search(request)
        return produce_result(results)
    except:
        return produce_exception()


def search(request):
    kw = request.POST
    if not kw:
        kw = request.GET
    kw = json.loads(kw['input_data'])
    args = kw['args']
    params = kw['params']
    search_text = params['kw'].lower()
    is_content_search = params.get('is_content_search')
    results = []
    search_models = params.get('search_models')
    if is_content_search:
        search_apps = {
            'documents':
                {
                    'file': ['content']
                }
        }
    else:
        search_apps = {
            'meetings':
                {
                    'Event': ['name', 'description'],
                    'Topic': ['name', 'lead'],
                    'Committee': ['name'],
                    'Profile': ['name', 'username', 'first_name', 'last_name', 'email'],

                    'MeetingDocument': ['name'],
                    'AgendaDocument': ['name'],

                    'News': ['name', 'description'],
                    'NewsDocument': ['name'],
                    'NewsVideo': ['name'],
                },
            'esign': {
                'SignatureDoc': ['name']
            },
            'resources':
                {
                    'Folder': ['name'],
                    'ResourceDocument': ['name']
                },
            'survey':
                {
                    'Survey': ['name', 'description'],
                    'Question': ['text']
                },
            'voting':
                {
                    'Voting': ['name', 'description'],
                    'VotingDocument': ['name'],
                    'VotingChoice': ['name'],
                    'VotingType': ['name']
                }
        }

    if search_models:
        for app_name in search_models:
            for model_name in search_models[app_name]:
                fields = search_apps[app_name][model_name]
                kwargs = {}
                q_objects = Q()
                for field in fields:
                    q_objects |= Q(**{field + '__contains': params['kw']})
                    kwargs.update({'{0}__{1}'.format(field, 'contains'): search_text})
                model_obj = apps.get_model(app_name, model_name)
                search_result = model_obj.objects.filter(q_objects)
                if search_result:
                    search_result = ws_methods.queryset_to_list_search(search_result)
                    for result in search_result:
                        result['model'] = app_name + '.' + model_name
                    results = results + search_result
        return results
    else:
        for app, models in search_apps.items():
            for model, fields in models.items():
                kwargs = {}
                q_objects = Q()
                for field in fields:
                    q_objects |= Q(**{field + '__contains': params['kw']})
                    kwargs.update({'{0}__{1}'.format(field, 'contains'): search_text})
                model_obj = apps.get_model(app, model)
                search_result = model_obj.objects.filter(q_objects)
                if search_result:
                    search_result = ws_methods.queryset_to_list_search(search_result)
                    for result in search_result:
                        result['model'] = app + '.' + model
                    results = results + search_result
        return results


@login_required()
def session(request):
    try:
        if request.user.id != 1:
            produce_result("unauthorized")
        kw = request.POST
        if not kw:
            kw = request.GET

        kw = json.loads(kw['input_data'])
        args = kw['args']
        params = kw['params']

        if not request.user.id:
            res = {'error': 'Invalid user'}
            return produce_result(res, args)

        model = apps.get_model(args['app'], args['model'])
        method_to_call = getattr(model, args['method'])
        res = method_to_call(request, params)
        return produce_result(res, args)
    except:
        return produce_exception()


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            errorMessage += " " + er
    return HttpResponse(errorMessage)


def produce_exception_public():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            errorMessage += " " + er
    res = {'error': errorMessage}
    res = json.dumps(res)
    return HttpResponse(res)


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
    try:
        res = json.dumps(res, cls=DjangoJSONEncoder)
    except:
        print(args)
        print('\n\n\n')
        print(res['data'])
        print('\n\n\n')
        return produce_exception()
        # dir = os.path.dirname(os.path.realpath(__file__))
        # ar = dir.split('/')
        # ar = ar[:-1]
        # dir = ('/').join(ar)
        # with open(dir + '/error_log.txt', "a+") as f:
        #     f.write(args + '\n\n' + res['data'])
    return HttpResponse(res)