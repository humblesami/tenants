from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from auth_t.models import TenantUser
from main_app.ws_methods import get_company_url
from website.models import PortalUser


def tenant_idex(request):
    template_name = "tenant_only/index.html"
    context = {}
    uid = request.user.id
    tenant_name = connection.tenant.name
    return render(request, template_name, context)


def token_login(request, token):
    logged_in = request.user.id
    user_tenant = connection.tenant
    url_to_go = '/'
    if not logged_in and token:
        connection.set_schema_to_public()
        ContentType.objects.clear_cache()
        portal_user = PortalUser.objects.filter(token=token)
        if portal_user:
            portal_user = portal_user[0]
            user_name = portal_user.username
            connection.set_tenant(user_tenant, False)
            ContentType.objects.clear_cache()
            user_list = TenantUser.objects.filter(username=user_name)
            if user_list:
                user = user_list[0]
                login(request, user)
                url_to_go = get_company_url(user_tenant.schema_name)
    uid = request.user.id
    tenant_name = connection.tenant.name
    return redirect(url_to_go)
