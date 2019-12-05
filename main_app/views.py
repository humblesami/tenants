from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from main_app.ws_methods import produce_exception
from django.contrib.auth import authenticate, login, logout


class Login(TemplateView):
    template_name = 'login.html'
    def get_context_data(self, **kwargs):
        context = {}
        return context


def authenticate_user(request):
    post_data = request.POST
    if request.method == 'GET':
        post_data = request.GET
    username = post_data.get('username')
    password = post_data.get('password')
    next_url = post_data.get('next_url') or '/'
    user = authenticate(request, username=username, password=password)
    if user and user.id:
        login(request, user)
        return redirect(next_url)
    else:
        context = {'error' : 'Invalid credentials'}
        return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    return redirect('/')

