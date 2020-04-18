from mainapp import ws_methods, settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    user = request.user
    context = {'uid': None}
    main_url = settings.MAIN_URL
    if user and user.id:
        context = {
            'uid': user.id,
            'name': ws_methods.get_user_name(user),
            'id': user.id,
            'main_url': main_url,
            'is_staff': user.is_staff,
            'home_url': request.home_url,
            'login': user.username
        }
    else:
        context = {
            'error': 'Invalid Access',
            'main_url': main_url
        }
    return render(request, 'index.html', context)