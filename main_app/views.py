from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from main_app.ws_methods import produce_exception
from django.contrib.auth import authenticate, login, logout


class Login(TemplateView):
    template_name = 'login.html'
    def get_context_data(self, **kwargs):
        context = {}
        return context


def authenticate_user(request):
    try:
        post_data = request.GET
        username = post_data.get('login')
        password = post_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.id:
            login(request, user)
            return HttpResponse('done')
        else:
            return HttpResponse('Invalid credentials')
    except:
        res = produce_exception()
        return HttpResponse(res)


def logout_user(request):
    try:
        logout(request)
        return redirect('/')
    except:
        res = produce_exception()
        return HttpResponse(res)

