import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import ContentType


class Command(BaseCommand):
    help = 'Sample permissions which will use as base file for Groups'

    def handle(self, *args, **kwargs):
        res = {}
        print('Please wait sample permissions are being created.')
        ctypes = ContentType.objects.prefetch_related('permission_set').all()
        for ctype in ctypes:
            try:
                if not res[ctype.app_label]:
                    res[ctype.app_label] = {}
            except:
                res[ctype.app_label] = {}

            res[ctype.app_label].update({
                ctype.model: {'add': 1, 'delete': 1, 'view': 1, 'change': 1}
            })
        with open('json_files/permissions_sample.json', 'w+') as outFile:
            jsonData = json.dumps(res)
            outFile.write(jsonData)
        print('Sample permissions are created.')




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