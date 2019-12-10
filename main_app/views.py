from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout


def login_page(request):
    template_name = 'login.html'
    context = {}
    if request.method == 'POST':
        post_data = request.POST
        username = post_data.get('username')
        password = post_data.get('password')
        next_url = post_data.get('next_url') or '/'
        user = authenticate(request, username=username, password=password)
        if user and user.id:
            login(request, user)
            return redirect(next_url)
        else:
            context = {'error': 'Invalid credentials', 'input': {'username': username, 'next_url': next_url}}
            return render(request, template_name, context)
    return render(request, template_name, context)


def logout_user(request):
    logout(request)
    return redirect('/')

