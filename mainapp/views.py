import os
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http.response import FileResponse, HttpResponse
from mainapp.settings import server_base_url
from mainapp.settings import MEDIA_ROOT

def serve_protected_document(request,folder, file):
    if not request.user.id:
        referer_address = request.META.get('HTTP_REFERER')
        if not referer_address:
            return ''
        if not referer_address.endswith('localhost:4200/'):
            return ''
    path = MEDIA_ROOT + '/' + folder + '/' +file
    response = FileResponse(open(path,'rb'))
    return response

def response_submitted(request):
    return render(request,'mainapp/response_submitted.html', {'server_base_url': server_base_url})