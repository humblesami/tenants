import urllib

from django import forms
from django.contrib import admin

from mainapp import ws_methods
from .models import Signature, SignatureDoc
from mainapp.admin import BaseAdmin
from meetings.model_files.event import Event


class SignatureAdmin(BaseAdmin):
    list_display = ['user', 'document', 'signed_at']

class SignDocForm(forms.ModelForm):
    class Meta:
            model = SignatureDoc
            fields = ()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meeting'].queryset = Event.objects.filter(archived=False)

    def clean(self):
        cleaned_data = super().clean()
        attachment = cleaned_data.get("attachment")
        cloud_url = cleaned_data.get("cloud_url")
        pdf_doc = cleaned_data.get("pdf_doc")
        access_token = cleaned_data.get("access_token")
        name = cleaned_data.get("name")

        if name:
            if not attachment and not cloud_url and not pdf_doc:
                msg = "No attachment provided"
                self.add_error('attachment', msg)
            elif pdf_doc:
                if not pdf_doc.url:
                    msg = "No attachment provided"
                    self.add_error('attachment', msg)
            elif cloud_url:
                try:
                    headers = {}
                    if access_token and access_token != 'Local':
                        headers = {'Authorization': 'Bearer ' + access_token}
                    request = urllib.request.Request(cloud_url, headers=headers)
                    request = None
                except urllib.error.HTTPError as e:
                    msg = str(e.code) + e.reason
                    self.add_error('attachment', msg)

class SignDocAdmin(BaseAdmin):
    form = SignDocForm
    list_display = ('name', 'meeting', 'send_to_all','created_by')
    fields = [
        'attachment',
        'name',
        'cloud_url',
        'access_token',
        'file_name',
        'meeting',
        'respondents',
        'send_to_all',
        'open_date',
        'close_date'
    ]
    autocomplete_fields = ['respondents']
    change_form_template = 'admin/actions_change_form.html'

    # def save_model(self, request, obj, form, change):
    #     try:
    #         super(SignDocAdmin, self).save_model(request, obj, form, change)
    #     except Exception as e:
    #         err = str(e)
    #         err = err.split('\n')
    #         last = len(err) - 1
    #         temp = err[last]
    #         if temp == '':
    #             last = last -1
    #             err = err[last]
    #         else:
    #             err = temp
    #         raise ValidationError(err)

    class Media:
        js = ('admin/js/esign_doc.js',)
        css = {
            'all': ('admin/css/esign-doc.css',)
        }

    # def save_model(self, request, obj, form, change):
    #     super(SignDocAdmin, self).save_model(request, obj, form, change)


# class SignatureDocForm(FileForm):
#     change_form_template = 'admin/actions_change_form.html'
#     # def get_form(self, request, obj=None, **kwargs):
#     #     kwargs['fields'] = ['name', 'attachment']
#     #     # self.exclude = ('original_pdf','workflow_enabled')
#     #     form = super(SignatureDocForm, self).get_form(request, obj, **kwargs)
#     #     return form

admin.site.register(SignatureDoc, SignDocAdmin)
admin.site.register(Signature, SignatureAdmin)
