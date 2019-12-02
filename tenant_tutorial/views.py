from django.db import utils
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

from customers.models import Client
from django.views.generic import TemplateView
from django_tenants.utils import remove_www
from django.views.defaults import page_not_found


# views.py
def custom_page_not_found(request):
    return page_not_found(request, None)

class HomeView(TemplateView):
    template_name = "index_public.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hostname_without_port = remove_www(self.request.get_host().split(':')[0])

        try:
            Client.objects.get(schema_name='public')
        except utils.DatabaseError:
            context['need_sync'] = True
            context['shared_apps'] = settings.SHARED_APPS
            context['tenants_list'] = []
            return context
        except Client.DoesNotExist:
            context['no_public_tenant'] = True
            context['hostname'] = hostname_without_port

        if Client.objects.count() == 1:
            context['only_public_tenant'] = True

        context['tenants_list'] = Client.objects.all()
        return context
