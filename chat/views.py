from django.http import HttpResponse

from chat.models import MessageDocument


def clear_moved(request):
    context = {}
    if request.user.is_superuser:
        MessageDocument.objects.all().update(moved=False)
    return HttpResponse('done')