from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    exclude = ('created_at', 'created_by', 'updated_at', 'updated_by')


class BaseInlineAdmin(admin.StackedInline):
    exclude = ('created_at', 'created_by', 'updated_at', 'updated_by')