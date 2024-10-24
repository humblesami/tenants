from django import forms
from .models import ClientTenant


class ClientTenantForm(forms.ModelForm):
    class Meta:
        model = ClientTenant
        widgets = {
        }