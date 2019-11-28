import sys
import traceback
from random import choice

from tenant_only.models import UploadFile
from customers.models import Client, Domain
from customers.forms import GenerateUsersForm

from django.db.utils import DatabaseError
from django.contrib.auth.models import User
from django_tenants.urlresolvers import reverse_lazy
from django.views.generic import FormView, TemplateView, CreateView


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    errorMessage = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            errorMessage += "==================" + er
    return errorMessage


def create_public_tenant():
    domain_url = 'domain.local'
    tenant = Client(schema_name='public',name='Schemas Inc.')
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here! on a local server you'll want to use localhost here
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()


def create_real_tenant(t_name):
    if not Client.objects.filter(schema_name='public'):
        create_public_tenant()
    if Client.objects.filter(schema_name=t_name):
        return 'Customer '+t_name+' Already exists'
    domain_url = t_name + '.localhost'
    tenant = Client(schema_name=t_name, name='Schemas '+t_name)
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = domain_url  # don't add your port or www here!
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    return ' Created customer '+t_name+' successfully '


class Create(TemplateView):
    template_name = "page1.html"

    def get_context_data(self, **kwargs):
        tenant_name = self.request.GET['name']
        res = 'Unknown status'
        try:
            res = create_real_tenant(tenant_name)
        except:
            res = produce_exception()
        context = {'p1': res}
        return context


class TenantView(TemplateView):
    template_name = "index_tenant.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants_list'] = Client.objects.all()
        return context


class TenantViewRandomForm(FormView):
    form_class = GenerateUsersForm
    template_name = "random_form.html"
    success_url = reverse_lazy('random_form')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants_list'] = Client.objects.all()
        context['users'] = User.objects.all()
        return context

    def form_valid(self, form):
        User.objects.all().delete()  # clean current users

        # generate five random users
        users_to_generate = 5
        first_names = ["Aiden", "Jackson", "Ethan", "Liam", "Mason", "Noah",
                       "Lucas", "Jacob", "Jayden", "Jack", "Sophia", "Emma",
                       "Olivia", "Isabella", "Ava", "Lily", "Zoe", "Chloe",
                       "Mia", "Madison"]
        last_names = ["Smith", "Brown", "Lee", "Wilson", "Martin", "Patel",
                      "Taylor", "Wong", "Campbell", "Williams"]

        while User.objects.count() != users_to_generate:
            first_name = choice(first_names)
            last_name = choice(last_names)
            try:
                user = User(username=(first_name+last_name).lower(),
                            email="%s@%s.com" % (first_name, last_name),
                            first_name=first_name,
                            last_name=last_name)
                user.save()
            except DatabaseError:
                pass

        return super().form_valid(form)


class TenantViewFileUploadCreate(CreateView):
    template_name = "upload_file.html"
    model = UploadFile
    fields = ['filename']
    success_url = reverse_lazy('upload_file')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants_list'] = Client.objects.all()
        context['upload_files'] = UploadFile.objects.all()
        return context

