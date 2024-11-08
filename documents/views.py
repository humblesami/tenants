import os
import json

from django.apps import apps
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.core.files import File as DjangoFile
from django.views.decorators.csrf import csrf_exempt

from .models import File
from sam_pytools import LogUtils, CoreUtils


@csrf_exempt
@api_view(["GET", "POST"])
def upload_files(request):
    docs = []
    try:
        req = request.POST
        res_app = req['res_app']
        res_model = req['res_model']
        res_id = req['res_id']
        model = apps.get_model(res_app, res_model)
        if res_id != 'undefined':
            obj = model.objects.get(pk=res_id)
        cloud_data = req.get('cloud_data')
        created_file = None
        with transaction.atomic():
            if cloud_data:
                cloud_data = json.loads(cloud_data)
                for file in cloud_data:
                    if res_app =='documents' and res_model == 'File':
                        created_file = model(name=file['name'], cloud_url=file['url'], file_type='temp',
                                                            file_name=file['file_name'])
                        created_file.save()
                    else:
                        if file['source']=='Google':
                            created_file = obj.documents.create(name=file['name'], cloud_url=file['url'], file_name=file['file_name'],access_token=file['access_token'])
                        else:
                            created_file = obj.documents.create(name=file['name'], cloud_url=file['url'], file_name=file['file_name'])
                    docs.append({'id':created_file.id, 'name': file['name'], 'access_token': created_file.access_token})
            for key in request.FILES:
                files = request.FILES.getlist(key)
                for file in files:
                    if res_app == 'documents' and res_model == 'File':
                        created_file = model(name=file.name, file_name=file.name, attachment=file, file_type='temp')
                        created_file.save()
                    else:
                        created_file = obj.documents.create(name=file.name, file_name=file.name, attachment=file)
                    docs.append({'id':created_file.id, 'name': file.name, 'access_token': "Local"})

        docs = json.dumps(docs)
    except:
        docs = LogUtils.get_error_json()
    return HttpResponse(docs)

@csrf_exempt
@api_view(["GET", "POST"])
def upload_single_file(request):   
    docs = []
    try:
        req = request.POST
        res_app = req['res_app']
        res_model = req['res_model']
        res_id = req['res_id']
        file_field = req['res_field']
        file_type = req['file_type']
        model = apps.get_model(res_app, res_model)
        obj = model.objects.get(pk=res_id)
        cloud_data = req.get('cloud_data')

        if cloud_data:
            cloud_data = json.loads(cloud_data)            
            for file in cloud_data:
                with transaction.atomic():
                    if file_type == 'image':
                        img_temp = PyUtils.download_image(file)
                        if type(img_temp) == str:
                            res = {
                                'error': {'data': img_temp, 'message': 'unable to upload file.'}
                            }
                            res = json.dumps(res)
                            return HttpResponse(res)
                        file_obj = getattr(obj, file_field)
                        file_obj.save(file['file_name'], DjangoFile(img_temp))
                        setattr(obj,file_field, file_obj)
                        obj.save()                        
                    else:    
                        created_file = File(name=file['name'], cloud_url=file['url'], file_name=file['file_name'])
                        created_file.save()
                        file_obj = getattr(obj, file_field)
                        file_obj = created_file
                        setattr(obj,file_field, file_obj)
                        obj.save()
                        docs.append({'id':created_file.id, 'name': file['name'], 'access_token': created_file.access_token})
        else:
            for key in request.FILES:
                files = request.FILES.getlist(key)
                for file in files:
                    with transaction.atomic():
                        created_file = File(name=file.name, file_name=file.name)
                        created_file.attachment.save(file.name, file)
                        created_file.save()
                        file_obj = getattr(obj, file_field)
                        file_obj = created_file
                        setattr(obj,file_field, file_obj)
                        if file_obj.id:
                            obj.save()
                        else:
                            res = LogUtils.get_error_json()
                            return {'error': {'data': res, 'message': 'unable to upload file.'}}
                        # created_file = obj.resume.attachment.save(name=file.name, attachment=file)
                        docs.append({'id':created_file.id, 'name': file.name, 'access_token': "Local"})

        docs = json.dumps(docs)
        return HttpResponse(docs)
    except:
        docs = LogUtils.get_error_json()
    return HttpResponse(docs)


@csrf_exempt
@api_view(["GET", "POST"])
def upload_single_image_file(request):   
    docs = []
    try:
        req = request.POST
        res_app = req['res_app']
        res_model = req['res_model']
        res_id = req['res_id']
        file_field = req['res_field']
        file_type = req['file_type']
        model = apps.get_model(res_app, res_model)
        obj = model.objects.get(pk=res_id)
        cloud_data = req.get('cloud_data')

        if file_type != 'image':
            docs = json.dumps(docs)
            return HttpResponse(docs)
        if cloud_data:
            cloud_data = json.loads(cloud_data)
            with transaction.atomic():
                for file in cloud_data:
                    if file_type == 'image':
                        img_temp = PyUtils.download_image(file)
                        if type(img_temp) == str:
                            res = {
                                'error': {'data': img_temp, 'message': 'unable to upload file.'}
                            }
                            res = json.dumps(res)
                            return HttpResponse(res)
                        file_obj = getattr(obj, file_field)
                        file_obj.save(file['file_name'], DjangoFile(img_temp))
                        setattr(obj,file_field, file_obj)
                        obj.save()
                        docs.append({'image_url':file_obj.url})
        else:
            with transaction.atomic():
                for key in request.FILES:
                    files = request.FILES.getlist(key)
                    for file in files:
                        if file_type == 'image':
                            curr_dir = os.path.dirname(__file__)
                            directory = curr_dir.replace('documents', 'media')
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            full_filename = os.path.join(directory, 'profile', file.name)
                            img_temp = open(full_filename, 'wb+')
                            for chunk in file.chunks():
                                img_temp.write(chunk)
                            file_obj = getattr(obj, file_field)
                            file_obj.save(file.name, DjangoFile(img_temp))
                            setattr(obj,file_field, file_obj)
                            obj.save()
                            file_obj = getattr(obj, file_field)
                            docs.append({'image_url':file_obj.url})
        docs = json.dumps(docs)
        return HttpResponse(docs)
    except:
        docs = LogUtils.get_error_json()
    return HttpResponse(docs)
