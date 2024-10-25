from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from authsignup.models import AuthUser
from restoken.models import PostUserToken
from authsignup.auth_medods import AuthMethods


def login_page(request, next=None):
    context = {'error': '', 'register_url': '/auth/register/', 'forgot_url': '/auth/forgot-password/'}
    if request.method == 'POST':
        res = AuthMethods.authenticate_user(request)
        if res.get('error'):
            context['error'] = res.get('error')
        elif res.get('auth_type'):
            return render(request, 'auth_otp.html', res)
    return render(request, 'login.html', context)


def register_page(request):
    context = {'error': '', 'loin_url': '/auth/login/', 'forgot_url': '/auth/forgot-password/'}
    if request.method == 'POST':
        res = AuthMethods.register_user(request)
        if res.get('error'):
            context['error'] = res.get('error')
        elif res.get('auth_type'):
            return render(request, 'auth_otp.html', res)
    return render(request, 'register.html', context)

def forgot_password_page(request):
    context = {'error': '', 'loin_url': '/auth/login/', 'register_url': '/auth/register/'}
    return render(request, 'forgot_password.html', context)

def reset_password_page(request, token):
    context = {'error': '', 'loin_url': '/auth/login/'}
    if not token:
        context['error'] = 'Invalid Token'
    user_token = PostUserToken.validate_token(token, do_not_expire=True)
    if not user_token:
        context['error'] = 'Invalid Token'
    return render(request, 'reset_password.html', context)


def login_top_page(request, next=None):
    context = {'error': '', 'loin_url': settings.LOGIN_URL}
    if request.method == 'POST':
        res = AuthMethods.verify_code(request)
        if res.get('error'):
            context['error'] = res.get('error')
        elif res.get('message') == 'code sent':
            return render(request, 'login_otp.html', context)
    return render(request, 'login_otp.html', context)


def logout_user(request):
    logout(request)
    redirect(request.login_url)


def ping(request):
    return HttpResponse('available')


def load_verify_code_page(request):
    context = {}
    username = request.session.get('username')
    if username:
        del request.session['username']
        user = AuthUser.objects.get(username=username)
        auth_type = user.two_factor_auth
        context = {
            'auth_type': auth_type,
            'uuid': user.id,
            'message': 'Please check your '+auth_type+' to get latest verification code just received'
        }
    return render(request, 'verify_code.html', context)


@csrf_exempt
@api_view(["GET", "POST"])
def verify_token(request):
    return HttpResponse('done')

