from django.shortcuts import render

def submit_email(request):
    context = {}
    return render(request, 'voting/submit_email.html', context)

def reset_password(request):
    context = {}
    return render(request, 'user/reset_password.html', context)
# Create your views here.
