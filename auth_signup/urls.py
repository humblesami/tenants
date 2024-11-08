from django.urls import include, path
from django.views.generic.base import TemplateView
from .views import logout

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("accounts/logout/", logout),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", TemplateView.as_view(template_name="profile.html")),
    path("i18n/", include("django.conf.urls.i18n")),
]
