from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.auth.models import ContentType
from django.contrib.auth.models import Group
from django.db import transaction
import json

class Command(BaseCommand):
    help = 'Load initial data fixture and assign permissions to the groups'

    def load_data_from_local_files(self):
        group_permissions_data = None
        with open('json_files/group_permissions.json', 'r') as gperms:
            group_permissions_data = json.load(gperms)
        return group_permissions_data

    def get_content_type_data(self):
        content_types_data = {}
        models_list = []
        ctypes = ContentType.objects.all()
        for ctype in ctypes:
            model_name = ctype.app_label + '.' + ctype.model
            if model_name not in models_list:
                models_list.append(model_name)
            try:
                if not content_types_data[ctype.app_label]:
                    content_types_data[ctype.app_label] = {}
            except:
                content_types_data[ctype.app_label] = {}
            content_types_data[ctype.app_label].update({
                ctype.model: ctype.id
            })
        return content_types_data, models_list

    def add_permissions(self):
        permissions_models_list = []
        group_permissions_data = self.load_data_from_local_files()
        content_types_data, content_type_models_list = self.get_content_type_data()
        try:
            print('\033[1m' + '\033[4m' + '\033[94m' + 'Please wait setting up group permissions...' + '\x1b[0m')
        except:
            pass
        with transaction.atomic():
            for group in group_permissions_data:
                obj_group = Group.objects.get(name=group)
                obj_group.permissions.clear()
                apps = group_permissions_data[group]
                for app in apps:
                    try:
                        print('\033[95m' + app + '\x1b[0m')
                    except:
                        print(app)

                    models = apps[app]
                    for model in models:
                        perms = models[model]
                        for key, val in perms.items():
                            try:
                                model_name = app + '.' + model
                                if model_name not in permissions_models_list:
                                    permissions_models_list.append(model_name)
                                if val:
                                    content_type_id = content_types_data[app][model]
                                    code_name = key + '_' + model
                                    obj_perm = Permission.objects.get(content_type_id=content_type_id, codename=code_name)
                                    obj_group.permissions.add(obj_perm)
                                    try:
                                        print('\t' + '- \033[32m' + key + '\x1b[0m ' + model +' - \033[1m \033[94m' + group + '\x1b[0m ' + '\033[32m' + u'\u2714' + '\x1b[0m')
                                    except:
                                        print('\t' + key +  model + group  + '.... ok ')

                                else:
                                    try:
                                        print('\t' + '- \033[91m' + key + '\x1b[0m ' + model +' - \033[1m \033[94m' + group + '\x1b[0m ' + '\033[91m' + u'\u2718' + '\x1b[0m')
                                    except:
                                        print('\t' + key + model + group + '.... left ')
                            except:
                                try:
                                    print('\t' + '- \033[93m' + key + '\x1b[0m ' + model +' - \033[1m \033[94m' + group + '\x1b[0m ' + '\033[91m' + u'\u2718' + ' error' + '\x1b[0m')
                                except:
                                    print('\t' + key + model + group + '.... error ')
            
        models_not_in_permission_set = list(set(content_type_models_list) - set(permissions_models_list))
        models_not_in_content_type_set = list(set(permissions_models_list) - set(content_type_models_list))

        if len(models_not_in_permission_set):
            print('models not in permissions set are ')
            print(models_not_in_permission_set)
        if len(models_not_in_content_type_set):
            print('models not in content type set are ')
            print(models_not_in_content_type_set)
        
        print('Permissions are set to the Groups')

    def add_arguments(self, parser):
        parser.add_argument('-f', '--fixtures', action='store_true', help='load fixtures')

    def handle(self, *args, **kwargs):
        fixtures = kwargs['fixtures']
        if fixtures:
            call_command('loaddata', 'website/fixtures/data.json')
        self.add_permissions()


####### list difference
####### file for sample permissions
######################## some code to generate data files ######################

        # perms = Permission.objects.all()
        # for perm in perms:
        #     print(perm.name)
        # res = {}
        # ctypes = ContentType.objects.all()
        # for ctype in ctypes:
        #     try:
        #         if not res[ctype.app_label]:
        #             res[ctype.app_label] = {}
        #     except:
        #         res[ctype.app_label] = {}
        #     res[ctype.app_label].update({
        #         ctype.model: ctype.id
        #     })
        #     with open('contents.txt', 'w+') as outFile:
        #         jsonData = json.dumps(res)
        #         outFile.write(jsonData)
        ###################################################################################
        # groups = Group.objects.all()
        # res = {}
        # ctypes = ContentType.objects.prefetch_related('permission_set').all()
        # for group in groups:
        #     try:
        #         if not res[group.name]:
        #             res[group.name] = {}
        #     except:
        #         res[group.name] = {}
        #     for ctype in ctypes:
        #         try:
        #             if not res[group.name][ctype.app_label]:
        #                 res[group.name][ctype.app_label] = {}
        #         except:
        #             res[group.name][ctype.app_label] = {}

        #         res[group.name][ctype.app_label].update({
        #             ctype.model: {'add': 1, 'delete': 1, 'view': 1, 'change': 1}
        #         })
        # with open('contents.txt', 'w+') as outFile:
        #     jsonData = json.dumps(res)
        #     outFile.write(jsonData)
        ##############################################################
        #     group.permissions.clear()
        #     group.permissions.add(*permissions)
        # print('Permissions Added')
        # print(root_dir)
        # with open('/meetings/fixtures/userdata.json', 'r') as inFile:
        #     print('file opened')
        # data = []
        # res = {}
        # ctypes = ContentType.objects.prefetch_related('permission_set').all()
        # for ctype in ctypes:
        #     permissions = []
        #     for permission in ctype.permission_set.all():
        #         permissions.append({
        #             'id': permission.id,
        #             'permission_name': permission.name
        #         })

            # if not res[ctype.app_name]:
            #     res[ctype.app_name] = {}
            # if not res[ctype.app_name][ctype.model_name]
            #     res[ctype.app_name][ctype.model_name] = {}
            

            # contentData = {
                
            # }

            # contentData = {
            #     'id': ctype.id,
            #     'name': ctype.name,
            #     'permissions': permissions
            # }
            # data.append(contentData)
            
        # with open('contents.txt', 'w+') as outFile:
        #     jsonData = json.dumps({'data': data})
        #     outFile.write(jsonData)
        # print('File Created')