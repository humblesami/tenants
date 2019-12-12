

from django.contrib import admin
from django.apps import apps

class CustomAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        # print(app_dict)
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
            for model in app['models']:
                # print(model)
                try:
                    model_obj = apps.get_model(app['app_label'], model['object_name'])
                    model['name'] += ' ({})'.format(model_obj.objects.count())
                except:
                    pass
        return app_list


class BaseAdmin(admin.ModelAdmin):
    exclude = ('created_at', 'created_by', 'updated_at', 'updated_by')


class BaseInlineAdmin(admin.StackedInline):
    exclude = ('created_at', 'created_by', 'updated_at', 'updated_by')