import re

from documents.file import File
from mainapp import ws_methods
from mainapp.models import CustomModel
from mainapp.settings import server_base_url

from django.db.models import Q
from django.db import transaction, models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django_currentuser.middleware import get_current_user


class Folder(CustomModel):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    users = models.ManyToManyField(User, related_name='folder_audience', blank=True)
    personal = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.name

    def get_accurate_name(self, user_id):
        name = self.name
        folder_with_same_name = Folder.objects.filter(
            ~Q(pk=self.pk) & Q(name=name) & Q(users__in=[user_id]))
        while folder_with_same_name:
            name = name + '_1'
            folder_with_same_name = Folder.objects.filter(
                ~Q(pk=self.pk) & Q(name=name) & Q(users__in=[user_id]))
        return name

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        creating = False
        name_updated = False
        if not self.pk:
            creating = True
            name_updated = True
        if not name_updated:
            same_name = Folder.objects.filter(Q(name=self.name) & ~Q(pk=self.pk))
            if same_name:
                self.name = self.get_accurate_name(current_user.id)
        super(Folder, self).save(*args, **kwargs)
        if creating and current_user not in self.users.all():
            name_updated = True
            self.users.add(current_user.id)
            self.save()

    def create_personal_folder(cls, request, params):
        personal_folder = None
        try:
            personal_folder = cls.objects.filter(personal=True, created_by_id=request.user.id)
            if not personal_folder:
                personal_folder = cls(name='My Documents', personal=True)
                personal_folder.save()
                personal_folder.users.add(request.user.id)
                personal_folder.save()
        except:
            if personal_folder:
                personal_folder.delete()

    def update_child_access(self, ids_to_remove, user_id):
        if self.id:
            documents = self.documents.all()
            for document in documents:
                for user in ids_to_remove:
                    if user != user_id:
                        document.users.remove(user)
            sub_folders = Folder.objects.filter(parent_id=self.id)
            if sub_folders:
                for sub_folder in sub_folders:
                    for user in ids_to_remove:
                        if user != user_id:
                            sub_folder.users.remove(user)
                    sub_folder.update_child_access(ids_to_remove, user_id)
        return 'done'

    @classmethod
    def create_new(cls, request, params):
        name = params['name']
        folder = Folder(
            name=name,
        )
        personal = False
        parent_id = params.get('parent_id')
        if parent_id:
            folder.parent_id = parent_id
            folder.personal = folder.parent.personal
        folder.save()
        data = {
            'name': folder.name,
            'id': folder.id,
            'parent': parent_id,
            'personal': folder.personal
        }
        return data

    @classmethod
    def delete_folder(cls, request, params):
        folder_id = params['folder_id']
        folder = Folder.objects.get(pk=folder_id)
        folder.delete()
        return 'done'

    @classmethod
    def is_valid_parent(cls, folder_id, target_folder_id):
        if folder_id:
            folder_id = int(folder_id)
        if target_folder_id:
            target_folder_id = int(target_folder_id)
        if folder_id == target_folder_id:
            return False
        target_folder_id = Folder.objects.get(pk=target_folder_id).parent_id
        if not target_folder_id:
            return True
        return cls.is_valid_parent(folder_id, target_folder_id)

    @classmethod
    def move_objects(cls, request, params):
        objects_to_move = params['objects_to_move']
        target_folder_id = params['folder_id']
        current_parent_id = objects_to_move['current_parent_id']
        if current_parent_id == target_folder_id:
            return 'done'
        file_ids = objects_to_move['files']
        folder_ids = objects_to_move['folders']
        for fid in folder_ids:
            can_be_aprent = cls.is_valid_parent(fid, target_folder_id)
            if not can_be_aprent:
                return 'Can not move a prent in its children'
        res = {'files':[], 'folders':[]}
        with transaction.atomic():
            for obj_id in file_ids:
                obj = ResourceDocument.objects.get(pk=obj_id)
                obj.folder_id = target_folder_id
                obj.save()
                file = {
                    'id': obj.id,
                    'name': obj.name,
                    'personal': obj.personal,
                    'access_token': obj.access_token
                }
                res['files'].append(file)
            for obj_id in folder_ids:
                obj = Folder.objects.get(pk=obj_id)
                obj.parent_id = target_folder_id
                obj.save()
                folder = {
                    'id': obj.id,
                    'name': obj.name,
                    'personal': obj.personal,
                }
                res['folders'].append(folder)
        return res

    @classmethod
    def get_my_folder_recursive(cls, request, params):
        user_id = request.user.id        
        parent_id = Folder.objects.get(created_by_id = user_id, personal=True, parent_id__isnull=True).id
        res = cls.folders_recursive_childs(user_id, parent_id)
        return res    
    
    @classmethod
    def folders_recursive_childs(cls, user_id, parent_id):
        res = {}
        if parent_id:
            folder = Folder.objects.filter(pk=parent_id, users__id=user_id).order_by('-pk')
            if folder:
                folder = folder[0]
                res = { 
                    'id': folder.id,
                    'name': folder.name,
                    'sub_folders': folder.folders_recursive_subchilds(folder, user_id)
                    }
        return res

    def folders_recursive_subchilds(self, folder, user_id):
        result = {}
        sub_folders = Folder.objects.filter(parent=folder.id, users__id=user_id)
        if sub_folders:
            for sub_folder in sub_folders:
                sub_folders_check = Folder.objects.filter(parent=sub_folder.id, users__id=user_id)
                result[sub_folder.id] = {
                            'id': sub_folder.id,
                            'name': sub_folder.name,
                            'parent_path': folder.id,
                            'sub_folders': sub_folder.folders_recursive_subchilds(sub_folder, user_id)
                        }
        return result

    @classmethod
    def change_folder_name(cls, request, params):
        folder_id = params['folder_id']
        name = params['name']
        folder = Folder.objects.get(pk=folder_id)
        folder.name = name
        folder.save()
        data = {
            'id': folder.id,
            'name': folder.name
        }
        return data

    @classmethod
    def search_folders(cls, request, params):
        result = {}
        parent_id = params.get('parent_id')
        user_id = request.user.id
        recursive = params.get('recursive')
        if recursive == 'false':
            recursive = None
        kw = params.get('kw')
        if not kw:
            kw = ''
        if parent_id:
            folder = Folder.objects.filter(pk=parent_id, users__id=user_id).order_by('-pk')
            if folder:
                folder = folder[0]
                folder_ids_to_move = params.get('folder_ids_to_move')
                current_parent_id = params.get('current_parent_id')
                result['can_be_parent'] = True
                if current_parent_id == parent_id:
                    result['can_be_parent'] = False
                else:
                    len_moving_folders = 0
                    if folder_ids_to_move:
                        len_moving_folders = len(folder_ids_to_move)
                    if len_moving_folders > 0:
                        for fid in folder_ids_to_move:
                            can_be_parent = cls.is_valid_parent(fid, parent_id)
                            if not can_be_parent:
                                result['can_be_parent'] = False
                                break
                result['folders'] = folder.search_folder(kw, user_id, [], 'folders', recursive)
                result['parents'] = cls.get_ancestors(cls, folder)
                result['id'] = folder.id
                result['name'] = folder.name
                personal = False
                if folder.personal and folder.created_by_id == user_id:
                    result['personal'] = folder.personal
                owner = False
                if folder.created_by_id == user_id:
                    owner = True
                result['owner'] = owner
        else:
            result['folders'] = cls.search_root(kw, user_id, [], 'folders', recursive)
        return result

    @classmethod
    def search_files(cls, request, params):
        result = {'files': []}
        parent_id = params.get('parent_id')
        user_id = request.user.id
        recursive = params.get('recursive')
        personal = False
        me = False
        if recursive == 'false':
            recursive = None
        kw = params.get('kw')
        if not kw:
            kw = ''
        if parent_id:
            folder = Folder.objects.filter(pk=parent_id, users__id=user_id).order_by('-pk')
            if folder:
                folder = folder[0]
                if folder.personal:
                    personal = folder.personal
                    if folder.created_by_id == request.user.id:
                        me = True
                result = folder.search_folder(kw, user_id, [], 'files', recursive)
        elif recursive:
            result = cls.search_root(kw, user_id, [], 'files', recursive)
        data = {
            'files': result,
            'personal': personal,
            'me': me
        }
        return data

    @classmethod
    def search_root(cls, kw, user_id, results, search_type, recursive=False):
        folders = Folder.objects.filter(parent_id=None, users__id=user_id).order_by('-personal', '-pk')
        if search_type == 'folders':
            records = []
            for folder in folders:
                folder.total_files = 0
                folder.files_in_folder(folder, user_id)
                total_files = folder.total_files
                owner = False
                if folder.created_by_id == user_id:
                    owner = True
                folder_obj = folder.__dict__
                if re.search(kw, folder_obj['name'], re.IGNORECASE):
                    personal = False
                    if folder_obj['personal'] and folder_obj['created_by_id'] == user_id:
                        personal = True
                    results.append({
                        'id': folder_obj['id'],
                        'name': folder_obj['name'],
                        'total_files': total_files,
                        'personal': personal,
                        'owner': owner
                    })
        if recursive:
            for obj in folders:
                results = obj.search_folder(kw, user_id, results, search_type, recursive)
        return results

    def search_folder(self, kw, user_id, results, search_type, recursive=False):
        obj = self
        if search_type == 'files':
            files = obj.documents.filter(users__id=user_id, name__icontains=kw).values('id', 'name', 'access_token','personal', 'created_by_id').order_by('-pk')
            for file in files:
                personal = False
                if file['personal'] and file['created_by_id'] == user_id:
                    personal = True
                results.append({
                    'id': file['id'],
                    'name': file['name'],
                    'access_token': file['access_token'],
                    'personal': personal
                })
        if search_type == 'folders' or recursive:
            folders = obj.folder_set.filter(users__id=user_id).order_by('-pk')
            records = []
            for folder in folders:
                folder.total_files = 0
                folder.files_in_folder(folder, user_id)
                total_files = folder.total_files
                owner = False
                if folder.created_by_id == user_id:
                    owner == True
                if search_type == 'folders':
                    folder_obj = folder.__dict__
                    if re.search(kw, folder_obj['name'], re.IGNORECASE):
                        personal = False
                        if folder_obj['personal'] and folder_obj['created_by_id'] == user_id:
                            personal = True
                        results.append({
                            'id': folder_obj['id'],
                            'name': folder_obj['name'],
                            'total_files': total_files,
                            'personal': personal,
                            'owner': owner
                        })
                if recursive:
                    folder.search_folder(kw, user_id, results, search_type, recursive)
        return results

    def get_ancestors(self, folder_orm):
        parents_list = []
        upper_folder = folder_orm.parent
        while upper_folder:
            parents_list.append({'name': upper_folder.name, 'id': upper_folder.id})
            upper_folder = upper_folder.parent
        parents_list.reverse()
        return parents_list

    total_files = 0
    def files_in_folder(self, folder, user_id):
        folder.total_files += self.documents.filter(users__id=user_id).count()
        for sub_folder in self.folder_set.all():
            new_folder = Folder.objects.get(pk=sub_folder.id)
            new_folder.files_in_folder(folder, user_id)

    @classmethod
    def get_records(cls, request, params):
        kw = params.get('kw')
        user_id = request.user.id
        folders = []
        parent_id = params.get('parent_id')
        if kw:
            folders = ws_methods.search_db({'kw': kw, 'search_models': {'resources': ['Folder']}})
            if parent_id:
                folders = folders.filter(Q(parent_id=parent_id) & Q(users__id=user_id))
            else:
                folders = folders.filter(Q(parent__isnull=True) & Q(users__id=user_id))
        else:
            if parent_id:
                folders = Folder.objects.filter(Q(parent_id=parent_id) & Q(users__id=user_id)).order_by('-pk','-personal')
            else:
                folders = Folder.objects.filter(Q(parent__isnull=True) & Q(users__id=user_id)).order_by('-pk','-personal')

        total_cnt = folders.count()
        offset = params.get('offset')
        limit = params.get('limit')
        records = []
        users_obj = User.objects.all().order_by('-pk')
        all_users = list(users_obj.values('id', 'name'))
        if limit:
            folders = folders[offset: offset + int(limit)]
        for folder in folders:
            folder.total_files = 0
            folder.files_in_folder(folder, user_id)
            total_files = folder.total_files
            cd = ws_methods.obj_to_dict(folder, fields=['name', 'id'])
            cd['total_files'] = total_files
            records.append(cd)
        current_cnt = len(records)
        res = {'records': records, 'total': total_cnt, 'count': current_cnt, 'users': all_users}
        return res

    @classmethod
    def resource_search_details(cls, request, params):
        kw = params.get('kw')
        user_id = request.user.id
        folders = None
        files = None
        if kw:
            folders = Folder.objects.filter(users__id=user_id, name__icontains=kw)
            files = ResourceDocument.objects.filter(users__id=user_id, name__icontains=kw)
        else:
            folders = Folder.objects.filter(users__id=user_id)
            files = ResourceDocument.objects.filter(users__id=user_id)
        folder_set = list(files.values('id', 'name'))
        files_set = list(files.values('id', 'name'))
        data = {
            'folders': folder_set,
            'files': files_set
        }
        return data

    def resource_invitation_email(self, audience, action=None):
        template_data = {
            'folder_id': self.id,
            'folder_name': self.name,
            'server_base_url': server_base_url
        }
        post_info = {}
        post_info['res_app'] = self._meta.app_label
        post_info['res_model'] = self._meta.model_name
        post_info['res_id'] = self.id
        if action:
            template_name = 'resources/removed_from_folder_email.html'
            token_required = False
        else:
            template_name = 'resources/added_to_folder_email.html'
            token_required = False
        email_data = {
            'subject': self.name,
            'audience': audience,
            'post_info': post_info,
            'template_data': template_data,
            'template_name': template_name,
            'token_required': token_required
        }
        ws_methods.send_email_on_creation(email_data)


def save_folder_users(sender, instance, action, pk_set, **kwargs):
    # if action == 'post_remove':
    #     removed_respondents = list(pk_set)
    #     instance.resource_invitation_email(removed_respondents, 'removed')
    if action == "post_add":
        new_added_respondets = list(pk_set)
        try:
            new_added_respondets.remove(get_current_user().id)
        except:
            pass
        if new_added_respondets:
            instance.resource_invitation_email(new_added_respondets)


m2m_changed.connect(save_folder_users, sender=Folder.users.through)


class ResourceDocument(File):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents')
    users = models.ManyToManyField(User, related_name='file_audience', blank=True)
    personal = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_attachments(cls, request, params):
        parent_id = params.get('parent_id')
        docs = File.objects.filter(folder_id=parent_id)
        docs = docs.values('id', 'name')
        docs = list(docs)
        return docs

    def get_accurate_name(self):
        file_with_same_name = ResourceDocument.objects.filter(folder_id=self.folder.id, name=self.name)
        if len(file_with_same_name) > 1:
            count = 0
            while file_with_same_name:
                count += 1
                file_name = self.name.split('.')
                if len(file_name) >= 2:
                    file_name[len(file_name) - 2] = file_name[len(file_name) - 2] + '-' + str(count)
                else:
                    file_name[len(file_name) - 1] = file_name[len(file_name) - 1] + '-' + str(count)
                diff_name = '.'.join(file_name)
                file_with_same_name = ResourceDocument.objects.filter(folder_id=self.folder.id, name=diff_name)
            return diff_name
        else:
            return self.name

    def save(self, *args, **kwargs):
        if not self.file_type:
            self.file_type = 'resource'
        current_user = get_current_user()
        creating = False
        name_updated = False
        if not self.pk:
            creating = True
            name_updated = True
            self.personal = self.folder.personal
        if not name_updated:
            self.name = self.get_accurate_name()
        super(ResourceDocument, self).save(*args, **kwargs)
        if creating and current_user not in self.users.all():
            name_updated = False
            self.users.add(current_user.id)
            self.save()

    @property
    def breadcrumb(self):
        folder_obj = self.folder
        data = []
        if folder_obj:
            data.append({'title': folder_obj.name, 'link': '/resource/' + str(folder_obj.id)})
            ancestors = Folder.get_ancestors(self, folder_obj)
            for ancestor in ancestors:
                data.append({'title': ancestor['name'], 'link': '/resource/' + str(ancestor['id'])})
        data.append({'title': 'Resources', 'link': '/resources'})
        data.reverse()
        return data