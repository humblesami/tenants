from django.shortcuts import render
from django.views.generic import TemplateView
from django_tenants.utils import get_tenant_model


class Index(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        my_tenants_list = get_my_tenants(self.request.user)
        context = {'list': my_tenants_list}
        return context

def get_my_tenants(user):
    user_id = user.id
    tenants_list = []
    if user_id:
        tenants_list = get_tenant_model().objects.filter(users__in=[user_id])
        # tenants_list = tenants_list.prefetch_related('domains').all()
        # tenants_list = list(tenants_list.values('id', 'schema_name'))
    return tenants_list