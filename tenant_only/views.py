from random import choice
from django.db.utils import DatabaseError
from django.contrib.auth.models import User
from django_tenants.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, FormView, CreateView

from tenant_only.models import UploadFile
from tenant_only.forms import GenerateUsersForm


class TenantView(TemplateView):
    template_name = "index_tenant.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TenantViewRandomForm(FormView):
    form_class = GenerateUsersForm
    template_name = "random_form.html"
    success_url = reverse_lazy('random_form')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context['upload_files'] = UploadFile.objects.all()
        return context
