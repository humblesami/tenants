from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from documents.annotation import AnnotationDocument
from mainapp import ws_methods
from django.db import transaction
from meetings.model_files.user import Profile
from documents.file import File
from django.core.files import File as DjangoFile
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
import urllib
import json
import os


@csrf_exempt
@api_view(["GET", "POST"])
def upload_files(request):
    docs = []
    try:
        req = request.POST
        res_app = req['res_app']
        res_model = req['res_model']
        res_id = req['res_id']
        model = ws_methods.get_model(res_app, res_model)
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
        docs = ws_methods.get_error_message()
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
        model = ws_methods.get_model(res_app, res_model)
        obj = model.objects.get(pk=res_id)
        cloud_data = req.get('cloud_data')

        if cloud_data:
            cloud_data = json.loads(cloud_data)            
            for file in cloud_data:
                with transaction.atomic():
                    if file_type == 'image':
                        img_temp = ws_methods.download_image(file)
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
                            res = ws_methods.get_error_message()
                            return {'error': {'data': res, 'message': 'unable to upload file.'}}
                        # created_file = obj.resume.attachment.save(name=file.name, attachment=file)
                        docs.append({'id':created_file.id, 'name': file.name, 'access_token': "Local"})

        docs = json.dumps(docs)
        return HttpResponse(docs)
    except:
        docs = ws_methods.get_error_message()
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
        model = ws_methods.get_model(res_app, res_model)
        obj = model.objects.get(pk=res_id)
        cloud_data = req.get('cloud_data')

        if file_type != 'image':
            docs = json.dumps(docs)
            return HttpResponse(docs)
            return {'error': 'Invalid'}
        if cloud_data:
            cloud_data = json.loads(cloud_data)
            with transaction.atomic():
                for file in cloud_data:
                    if file_type == 'image':
                        img_temp = ws_methods.download_image(file)
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
        docs = ws_methods.get_error_message()
    return HttpResponse(docs)


def reset_annotations(request):
    try:
        if request.user.is_superuser:
            id = request.GET['id']
            code = request.GET['code']
            user_id = request.GET['for']
            if user_id == 'me':
                user_id = request.user.id
            if code != 't5g':
                return HttpResponse('Invalid code')
            docs = []
            if user_id == 'all':
                docs = AnnotationDocument.objects.filter(document__id=id)
            else:
                docs = AnnotationDocument.objects.filter(document__id=id, user__id=user_id)
            with transaction.atomic():
                for doc in docs:
                    for obj in doc.annotation_set.all():
                        obj.delete()
            return HttpResponse('done')
        else:
            return HttpResponse('Unauthorized')
    except:
        return HttpResponse('Error')