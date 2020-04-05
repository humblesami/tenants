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
