from django.contrib import admin
from documents.admin import FileAdmin, FileInlineAdmin
from .models import Folder, ResourceDocument
import nested_admin
from mainapp.admin import BaseInlineAdmin, BaseAdmin


class FolderInline(BaseInlineAdmin):
    model = Folder
    autocomplete_fields = ['users']
    show_change_link = True
    verbose_name = "Sub Folder"
    verbose_name_plural = "Sub Folders"
    extra = 1


class FileInline(FileInlineAdmin):
    model = ResourceDocument
    autocomplete_fields = ['users']
    show_change_link = True
    extra = 0


class FolderAdmin(BaseAdmin):
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'users'
            ]
        })
    ]
    autocomplete_fields = ['users']
    search_fields = ['name']
    readonly_fields = ['parent',]
    inlines = [FolderInline]
    def get_queryset(self, request):
        qs = super(FolderAdmin, self).get_queryset(request)
        if request.path =='/admin/resources/folder/':
            qs = qs.filter(parent=None)
        return qs


class ResourceDocAdmin(FileAdmin):
    autocomplete_fields = ['users', 'folder']

admin.site.register(Folder, FolderAdmin)
admin.site.register(ResourceDocument, ResourceDocAdmin)