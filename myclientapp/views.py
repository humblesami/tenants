from django.http import HttpResponse
from django.shortcuts import render

def root_view(request):
    return render(request, 'hello hh')
    # return HttpResponse('Hoello Root')