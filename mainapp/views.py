import uuid

from django.shortcuts import redirect, render
from django.http.response import FileResponse
from django_tenants.utils import get_tenant_model
from django.contrib.auth import authenticate, login, logout

from website.models import UserAuthToken
from mainapp.settings import MEDIA_ROOT
from mainapp.settings import server_base_url
from mainapp.ws_methods import get_company_url


def login_page(request):
    template_name = 'login.html'
    context = {}
    logout(request)
    if request.method == 'POST':
        post_data = request.POST
        username = post_data.get('username')
        password = post_data.get('password')
        next_url = post_data.get('next_url') or '/'
        user = authenticate(request, username=username, password=password)
        if user and user.id:
            login(request, user)
            if not user.is_staff:
                tenant_model = get_tenant_model()
                tenants_list = tenant_model.objects.filter(users__email__in=[user.email]).exclude(schema_name='public')
                if len(tenants_list) > 1:
                    return redirect('/clients/my-companies')
                else:
                    if len(tenants_list) == 1:
                        my_company = tenants_list[0]
                        auth_token = uuid.uuid4().hex[:20]
                        UserAuthToken.objects.create(username=user.username, token=auth_token)
                        auth_token = '/login/'+auth_token
                        url = get_company_url(my_company.schema_name)
                        return redirect(url+auth_token)
            return redirect('/')
        else:
            context = {'error': 'Invalid credentials', 'input': {'username': username, 'next_url': next_url}}
            return render(request, template_name, context)
    return render(request, template_name, context)


def tenant_login(request):
    logout(request)
    return redirect(request.login_url)


def tenant_logout(request):
    logout(request)
    return redirect(request.main_url + '/logout')


def logout_user(request):
    logout(request)
    return redirect('/')


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