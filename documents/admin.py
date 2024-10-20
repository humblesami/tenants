from django.contrib import admin
from dj_utils.admin import BaseAdmin, BaseInlineAdmin
from .models import File


class FileAdmin(BaseAdmin):
    list_display = ['id', 'name', 'upload_status', 'file_type', 'pdf_doc', 'upload_status', 'updated_by', 'html']
    exclude = ('created_at', 'created_by', 'updated_at', 'updated_by', 'file_type', 'content', 'pdf_doc', 'upload_status', 'html')


class FileInlineAdmin(BaseInlineAdmin):
    extra = 0
    exclude = (
        'created_at', 'created_by', 'updated_at', 'updated_by', 'file_type', 'file_input', 'content',
        'pdf_doc', 'upload_status', 'html','cloud_url', 'access_token', 'file_name'
    )


admin.site.register(File, FileAdmin)
