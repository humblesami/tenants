from django.urls import path
from tenant_only.views import TenantView, TenantViewRandomForm, TenantViewFileUploadCreate

urlpatterns = [
    path('', TenantView.as_view(), name="index"),
    path('random/', TenantViewRandomForm.as_view(), name="random_form"),
    path('upload/', TenantViewFileUploadCreate.as_view(), name="upload_file"),
]