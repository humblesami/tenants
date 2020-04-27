import uuid

from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect, render
from django_tenants.utils import get_tenant_model

from authentication.models import UserAuthToken
from main_app.ws_methods import get_company_url


def login_view(request):
    template_name = 'authentication/login.html'
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
                    return redirect('/')
                else:
                    if len(tenants_list) == 1:
                        my_company = tenants_list[0]
                        auth_token = uuid.uuid4().hex[:20]
                        UserAuthToken.objects.create(username=user.username, token=auth_token)
                        auth_token = '/login/'+auth_token
                        home_url = get_company_url(my_company.schema_name)
                        return redirect(home_url+auth_token)
            return redirect('/')
        else:
            context = {'error': 'Invalid credentials', 'input': {'username': username, 'next_url': next_url}}
            return render(request, template_name, context)
    return render(request, template_name, context)


def logout_view(request):
    logout(request)
    return redirect(request.login_url)

