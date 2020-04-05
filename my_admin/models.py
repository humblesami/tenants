from django.db import models
from django.apps import apps
from mainapp import ws_methods


class Helper(models.Model):

    @classmethod
    def define_access(cls, request, params):
        object_id = params.get('object_id')
        app_name = params['app']
        model_name = params['model']
        model = apps.get_model(app_name, model_name)

        user_id = request.user.id
        user_ids = params['user_ids']

        obj = model.objects.get(pk=object_id)

        old_user_ids = []
        id_list = obj.users.all().values('id')
        for id_obj in id_list:
            old_user_ids.append(id_obj['id'])

        for user in obj.users.all():
            if user.id != user_id and obj.created_by.id != user.id:
                obj.users.remove(user.id)
        obj.save()

        for uid in user_ids:
            if uid != user_id and obj.created_by.id != uid:
                obj.users.add(uid)
        obj.save()

        if model_name == 'Folder':
            removed_ids = set(old_user_ids).difference(user_ids)
            if len(removed_ids) > 0:
                obj.update_child_access(removed_ids, user_id)
        return 'done'

    @classmethod
    def rename_item(cls, request, params):
        item_id = params['item_id']
        name = params['name']

        app_name = params['app']
        model_name = params['model']
        model = apps.get_model(app_name, model_name)

        item = model.objects.get(pk=item_id)
        item.name = name
        item.save()
        data = {
            'id': item.id,
            'name': item.name
        }
        return data

    @classmethod
    def get_resource_audience(cls, request, params):
        object_id = params.get('object_id')
        app_name = params['app']
        model_name = params['model']

        parent = params.get('parent')
        audience = []
        has_admin_group = request.user.groups.filter(name='Admin')
        if not has_admin_group:
            return audience

        model = apps.get_model(app_name, model_name)
        users = model.objects.get(pk=object_id).users.all()
        audience = list(users.values('id', 'authuser__name'))
        audience = ws_methods.replace_key_in_dict(audience,'authuser__name', 'name')

        valid_audience = []
        if parent:
            parent_model = parent.get('model')
            parent_app = parent.get('app')
            parent_id = parent.get('id')

            app_name = parent_app
            model_name = parent_model
            model = apps.get_model(app_name, model_name)

            users = model.objects.get(pk=parent_id).users.all()
            # valid_audience = list(users.values('id', 'name', 'image'))
            valid_audience = ws_methods.queryset_to_list(users, ['id', 'authuser__name', 'authuser__image'])
            valid_audience = ws_methods.replace_key_in_dict(valid_audience,'authuser__name', 'name')
            valid_audience = ws_methods.replace_key_in_dict(valid_audience,'authuser__image', 'image')

        res = {'selected': audience, 'valid': valid_audience}
        return res
