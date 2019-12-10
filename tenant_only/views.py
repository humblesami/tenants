from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import TemplateView

from auth_t.models import TenantUser
from website.models import PortalUser


class Index(TemplateView):
    template_name = "tenant_only/index.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context


class TokenIndex(TemplateView):
    template_name = "tenant_only/index.html"

    def dispatch(self, request, *args, **kwargs):
        logged_in = request.user.id
        has_token = kwargs.get('token')
        user_tenant = connection.tenant
        if not logged_in and has_token:
            connection.set_schema_to_public()
            ContentType.objects.clear_cache()
            portal_user = PortalUser.objects.filter(token=kwargs['token'])
            if portal_user:
                portal_user = portal_user[0]
                user_name = portal_user.username
                connection.set_tenant(user_tenant, False)
                ContentType.objects.clear_cache()
                user_list = TenantUser.objects.filter(username=user_name)
                if user_list:
                    user = user_list[0]
                    login(self.request, user)
        return redirect('/')
