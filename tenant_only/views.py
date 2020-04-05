import json

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import TemplateView

from authsignup.models import AuthUser
from website.models import UserAuthToken


class Index(TemplateView):
    template_name = "tenant_only/index.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context


class TokenIndex(TemplateView):
    # template_name = "tenant_only/index.html"
    template_name = "authsignup/verify_code.html"

    def get_context_data(self, **kwargs):
        context = {}
        request = self.request
        has_token = kwargs.get('token')
        user_tenant = connection.tenant
        if has_token:
            connection.set_schema_to_public()
            ContentType.objects.clear_cache()
            portal_user = UserAuthToken.objects.filter(token=kwargs['token'])
            if portal_user:
                portal_user = portal_user[0]
                user_name = portal_user.username
                connection.set_tenant(user_tenant, False)
                ContentType.objects.clear_cache()
                user_list = AuthUser.objects.filter(username=user_name)
                if user_list:
                    user = user_list[0]
                    context = AuthUser.do_login(request, user, user.name)
        context = json.dumps(context)
        return { 'auth_user_data': context}
