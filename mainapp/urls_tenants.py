from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView

from mainapp.views import tenant_logout, tenant_login
from mainapp import rest_api
from tenant_only.views import token_index
from .import views

urlpatterns = [
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/favicon.ico')),
    path('login/<token>', token_index, name="index"),
    path('accounts/login', tenant_login, name = 'go to login page'),
    path('logout', tenant_logout),
    path('admin/', admin.site.urls),
    url(r'', include('ngapp.urls')),
    #tobe changed
    # url(r'^sw.js', (TemplateView.as_view(template_name="sw.js", content_type='application/javascript', )), name='sw.js'),
    path('rest/public', rest_api.public, name = 'public'),
    path('rest/secure', rest_api.secure, name = 'secure'),
    path('rest/secure1', rest_api.session, name = 'session'),
    path('rest/search', rest_api.search_ws, name = 'search_ws'),
    path('rest/search1', rest_api.search_session, name = 'search_session'),
    path('media/<str:folder>/<str:file>/', views.serve_protected_document, name='serve_protected_document'),

    url(r'^user/', include('authsignup.urls')),
    url(r'^', include('documents.urls')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url('auth-code/', include('authcode.urls')),
    url(r'^mail/', include('emailthread.urls')),
    url(r'^chat/', include('chat.urls')),
]