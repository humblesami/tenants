import os
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.apps import apps
from django.contrib import admin

from mainapp import ws_methods
from documents.file import File
from authsignup.models import AuthUser


class PostAddress(models.Model):
    res_app = models.CharField(max_length=128)
    res_model = models.CharField(max_length=128)
    res_id = models.IntegerField()


class NotificationType(models.Model):
    name = models.CharField(max_length=100, default='Unknown')
    template = models.CharField(max_length=256, default='')


class Notification(models.Model):
    post_address = models.ForeignKey(PostAddress, on_delete=models.CASCADE, null=True)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.post_address.res_app + '.' + self.post_address.res_model + '.' + str(
            self.post_address.res_id) + '--' + self.notification_type.name

    def get_meta(self, res_obj):
        # sender list would be same for all users/audience
        user_notifications = self.usernotification_set.filter(read=False, notification_id=self.id)
        senders_list = []
        for user_notification in user_notifications:
            sender = {
                'id': user_notification.sender.id,
                'name': user_notification.sender.name
            }
            if sender not in senders_list:
                senders_list.append(sender)

        notification_template = self.notification_type.template
        name_place = ''
        post_meta = None
        try:
            name_place = res_obj.notification_text()
            if hasattr(res_obj, 'get_meta'):
                post_meta = res_obj.get_meta()
        except:
            name_place = res_obj.name
        meta = {
            'senders': senders_list,
            'template': notification_template,
            'name_place': ' => ' + name_place,
            'info': post_meta
        }
        from string import Template

        notif = Template('$sender $template $name_place')
        senderText = ''
        senders = [sender['name'] for sender in senders_list]
        if len(senders) > 3:
            senderText = ', '.join(senders[:3]) + ' and ' + str(len(senders) -3) + ' other user'
        elif len(senders) > 2:
            senderText = ', '.join(senders[:len(senders)-1]) + ' and ' + str(senders[len(senders)-1: len(senders)][0])
        elif len(senders) == 2:
            senderText = senders[0] + ' and ' + senders[1]
        elif len(senders):
            senderText = senders[0]
            
        meta['text'] = notif.safe_substitute(sender=senderText , template=notification_template, name_place=name_place.strip())
        return meta

    @classmethod
    def mark_read(cls, request, params):
        notification_id = params['notification_id']
        notification = Notification.objects.get(id=notification_id)
        address = notification.post_address
        notifications = address.notification_set.all()
        read_ids = []
        for obj1 in notifications:
            user_notifications = obj1.usernotification_set.filter(user_id=request.user.id, read=False, notification_id=obj1.id)
            for obj3 in user_notifications:
                obj3.read = True
                obj3.save()
                if not obj1.id in read_ids:
                    read_ids.append(obj1.id)
        return read_ids

    @classmethod
    def add_notification(cls, sender, params, event_data, mentioned_list=None):
        type_name = params['notification_type']
        file_type = params.get('file_type')
        res_model = params['res_model']
        res_app = params['res_app']
        res_id = params['res_id']

        post_address = cls.get_post_address(res_app, res_model, res_id)
        if mentioned_list:
            mention_notification_type = cls.get_notification_type('mention')
            mention_notification = cls.get_notification(mention_notification_type.id, post_address.id)

        notification_type = cls.get_notification_type(type_name)
        notification = cls.get_notification(notification_type.id, post_address.id)

        model = apps.get_model(res_app, res_model)
        obj_res = model.objects.get(pk=res_id)
        audience = None
        try:
            audience = obj_res.get_audience()
        except:
            return 'get audience not defined for ' + res_app + '.' + res_model
        if not audience:
            return 'No Audience'
        if sender.id in audience:
            audience.remove(sender.id)
        senders_for_mention = {}
        count = 0
        if mentioned_list:
            for uid in mentioned_list:
                user_notification = UserNotification(notification_id=mention_notification.id, sender_id=sender.id, user_id=uid)
                user_notification.save()
                senders_for_mention[uid], count = UserNotification.get_senders(cls, uid, mention_notification.id)
            audience = list(set(audience) - set(mentioned_list))
        senders_for_all = {}
        for uid in audience:
            user_notification = UserNotification(notification_id=notification.id, sender_id=sender.id, user_id=uid)
            user_notification.save()
            senders_for_all[uid], count = UserNotification.get_senders(cls, uid, notification.id)

        meta = notification.get_meta(obj_res)
        # text = ' ' + meta['template'] + ' ' + meta['name_place']
        if len(audience) > 0:
            client_object = {
                'id': notification.id,
                'body': meta['text'],
                'senders': senders_for_all,
                'notification_type': notification_type.name,
                'address': {
                    'res_id': post_address.res_id,
                    'res_model': post_address.res_model,
                    'res_app': post_address.res_app,
                    'info': meta['info']
                }
            }
            events = [
                {'name': 'notification_received', 'data': client_object, 'audience': audience},
            ]
            if mentioned_list:
                mention_meta = mention_notification.get_meta(obj_res)
                clone = client_object.copy()
                clone['id'] = mention_notification.id
                clone['audience'] = mentioned_list
                clone['senders'] = senders_for_mention
                clone['notification_type'] = mention_notification_type.name
                clone['body'] = mention_meta['text']
                events.append({'name': 'notification_received', 'data': clone, 'audience': mentioned_list})
                emit_data = {
                    'name': event_data['name'],
                    'data': event_data['data'],
                    'audience': audience + mentioned_list
                }
                events.append(emit_data)
            else:
                events.append({'name': event_data['name'], 'data': event_data['data'], 'audience': audience})
            res = ws_methods.emit_event(events)
        else:
            return 'No audience for the notification'
        return res

    @classmethod
    def get_notification_type(cls, name):
        notification_type = NotificationType.objects.filter(name=name)
        template = ''
        if name == 'comment':
            template = 'commented on'
        elif name == 'mention':
            template = 'mentioned you in'
        else:
            template = name
        if not notification_type:
            notification_type = NotificationType(name=name, template=template)
            notification_type.save()
        else:
            notification_type = notification_type[0]
        return notification_type

    @classmethod
    def get_post_address(cls, res_app, res_model, res_id):
        post_address = PostAddress.objects.filter(res_app=res_app, res_model=res_model, res_id=res_id)
        if not post_address:
            post_address = PostAddress(res_app=res_app, res_model=res_model, res_id=res_id)
            post_address.save()
        else:
            post_address = post_address[0]
        return post_address

    @classmethod
    def get_notification(cls, notification_type_id, post_address_id):
        notification = Notification.objects.filter(notification_type_id=notification_type_id,
                                                   post_address_id=post_address_id)
        if not notification:
            notification = Notification(notification_type_id=notification_type_id, post_address_id=post_address_id)
            notification.save()
        else:
            notification = notification[0]
        return notification


class UserNotification(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    sender = models.ForeignKey(AuthUser, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='User')
    read = models.BooleanField(default=False)

    def get_senders(self, user_id, notification_id):
        notification_senders = UserNotification.objects.filter(
            read=False, user_id=user_id, notification_id=notification_id
        ).values('sender__id', 'sender__name')
        count = notification_senders.count()
        notification_senders = notification_senders.distinct()
        senders = []
        for notification_sender in notification_senders:
            senders.append({
                'id': notification_sender['sender__id'],
                'name': notification_sender['sender__name']
            })
        return senders, count

    @classmethod
    def mark_read_notification(cls, request, params):
        res_id = params['res_id']
        res_model = params['res_model']
        res_app = params['res_app']

        read_ids = []
        address = PostAddress.objects.filter(res_app=res_app, res_model=res_model, res_id=res_id)
        if address:
            address = address[0]
            notifications = address.notification_set.all()
            for obj1 in notifications:
                user_notifications = obj1.usernotification_set.filter(user_id=request.user.id, read=False, notification_id=obj1.id)
                for obj3 in user_notifications:
                    obj3.read = True
                    obj3.save()
                    if not obj1.id in read_ids:
                        read_ids.append(obj1.id)
        return read_ids

    @classmethod
    def get_my_notifications(cls, request, params):
        uid = request.user.id
        objects = {}
        notification_ids = []
        records = UserNotification.objects.filter(read=False, user_id=uid)

        not_found = {}
        for un in records:
            notification = un.notification
            if objects.get(notification.id):
                continue

            notification_ids.append(notification.id)
            notification_type = notification.notification_type.name

            address = notification.post_address
            model = apps.get_model(address.res_app, address.res_model)
            obj_res = model.objects.filter(pk=address.res_id)
            if obj_res:
                obj_res = obj_res[0]
                meta = notification.get_meta(obj_res)
                senders_for_all = {}
                senders_for_all[request.user.id], count = UserNotification.get_senders(cls, uid, notification.id)
                # text = ' ' + meta['template'] + ' ' + meta['name_place']
                client_object = {
                    'id': notification.id,
                    'count': count,
                    'body': meta['text'],
                    'senders': senders_for_all,
                    'notification_type': notification_type,
                    'address': {
                        'res_id': address.res_id,
                        'res_model': address.res_model,
                        'res_app': address.res_app,
                        'info': meta['info']
                    }
                }
                objects[notification.id] = client_object
            else:
                not_found[notification.id] = address.res_id
        array = []
        for key, item in objects.items():
            array.append(item)
        res = {'ids': notification_ids, 'list': array, 'objects': objects, 'not_found': not_found}
        return res


class Comment(models.Model):
    res_id = models.IntegerField()
    res_app = models.CharField(max_length=128)
    res_model = models.CharField(max_length=128)
    subtype_id = models.IntegerField()
    body = models.TextField()
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    create_date = models.DateTimeField(null=True, auto_now_add=True)

    @classmethod
    def get_comments(cls, request, params):
        if params.get('subtype_id'):
            res = cls.objects.filter(
                res_app=params['res_app'],
                res_model=params['res_model'],
                res_id=params['res_id'],
                subtype_id=params['subtype_id'],
            )
        else:
            res = cls.objects.filter(
                res_app=params['res_app'],
                res_model=params['res_model'],
                res_id=params['res_id'],
            )

        sql = "select un.id from chat_usernotification un "
        sql += " join chat_sendernotification sn on sn.id = un.sender_notification_id"
        sql += " join chat_notification n on sn.notification_id=n.id"
        sql += " join chat_postaddress pa on pa.id=n.post_address_id"
        sql += " where pa.res_app='meetings' and res_model='event' and res_id=1"
        # objs = UserNotification.objects.raw(sql)

        # with connection.cursor() as cursor:
        #     cursor.execute(sql)
        #     row = cursor.fetchall()

        # sql1 = "update chat_usernotification set read=True where id in("+sql+")"

        # with connection.cursor() as cursor:
        #     cursor.execute(sql1)
        #     row = cursor.fetchone()

        # objs = UserNotification.objects.raw(sql)
        parents = {

        }

        read_ids = []  # UserNotification.mark_read_notification(request, params)
        comments = []
        for obj in res:
            user = obj.user
            comment = obj.__dict__
            del comment['_state']
            ws_methods.stringify_fields(comment)
            comment['user'] = {
                'id': user.id,
                'photo': user.image.url,
                'name': user.name
            }
            comment['create_date'] = str(comment['create_date'])
            comment['children'] = []
            parents[comment['id']] = comment
            pk = comment['parent_id']
            if not pk:
                parents[pk] = comment
                comments.append(comment)
            else:
                parents[pk]['children'].append(comment)
        comments.reverse()
        res = comments
        res = {'comments': comments, 'read_notification_ids': read_ids}
        return res

    @classmethod
    def add(cls, request, params):
        mentioned_list = params.get('mentioned_list')
        user = AuthUser.objects.get(pk=request.user.id)
        comment = Comment(
            res_app=params['res_app'],
            res_model=params['res_model'],
            res_id=params['res_id'],
            subtype_id=params['subtype_id'],
            body=params['body'],
            user_id=user.id,
            create_date=datetime.now()
        )
        if params.get('parent_id'):
            comment.parent_id = params['parent_id']
        comment.save()
        comment = comment.__dict__
        comment['user'] = {
            'id': user.id,
            'photo': user.image.url,
            'name': user.name
        }
        del comment['_state']
        ws_methods.stringify_fields(comment)
        comment['create_date'] = str(datetime.now())
        comment['children'] = []
        param = params
        param['notification_type'] = 'comment'
        event_data = {'name': 'comment_received', 'data': comment, 'uid': request.user.id}
        Notification.add_notification(request.user, param, event_data, mentioned_list)
        return comment


class ChatGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(AuthUser, related_name='chat_groups')
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(AuthUser, null=True, on_delete=models.SET_NULL, related_name='group_owner', related_query_name='group_owner')
    create_time = models.DateTimeField(null=True, auto_now_add=True)
    created_by = models.ForeignKey(AuthUser, on_delete=models.CASCADE, null=True)

    @classmethod
    def create(cls, request, params):
        uid = request.user.id
        me_added = False
        member_ids = []
        for obj in params.get('members'):
            member_ids.append(obj['id'])
        chat_group = ChatGroup(
            name=params['name'],
            created_by_id=uid,
            owner_id = uid
        )
        chat_group.save()
        if not me_added:
            member_ids.append(uid)
        chat_group.members.set(member_ids)
        chat_group.save()

        owner = chat_group.owner
        created_chat_group = {
            'name': params['name'],
            'id': chat_group.id,
            'members': params.get('members'),
            'owner': {
                'id': uid,
                'name': owner.fullname(),
                'image': owner.image.url
            }
        }
        events = [
            {'name': 'chat_group_created', 'data': created_chat_group, 'audience': member_ids}
        ]
        res = ws_methods.emit_event(events)
        if res == 'done':
            return {'error': '', 'data': created_chat_group}
        else:
            return res

    @classmethod
    def update_members(cls, request, params):
        uid = request.user.id
        member_ids = []
        group_id = params['group_id']
        for obj in params.get('members'):
            member_ids.append(obj['id'])

        chat_group = ChatGroup.objects.get(pk=group_id)
        chat_group.members.set(member_ids)
        chat_group.save()

        group_members = []
        for mem in chat_group.members.all():
            group_members.append({
                'id': mem.id,
                'name': mem.name,
                'photo': mem.image.url,
            })
        group = {
            'id': chat_group.id,
            'name': chat_group.name,
            'members': group_members,
            'created_by': {
                'id': chat_group.created_by.id,
                'name': chat_group.created_by.name,
                'photo': chat_group.created_by.image.url,
            },
            'is_group': True,
            'create_time': str(chat_group.create_time),
        }

        event1 = {
            'name': 'chat_group_members_updated',
            'data': group,
            'audience': member_ids
        }
        events = [event1]
        res = ws_methods.emit_event(events)
        if res == 'done':
            return {'error': '', 'data': group}
        else:
            return res

    @classmethod
    def add_members(cls, request, params):
        audience = []
        uid = request.user.id
        member_ids = []
        group_id = params['group_id']
        for obj in params.get('members'):
            member_ids.append(obj['id'])
            audience.append(obj['id'])

        chat_group = ChatGroup.objects.get(pk=group_id)
        existing_members_ids = []
        for mem in chat_group.members:
            existing_members_ids.append(mem.id)
        member_ids = member_ids + existing_members_ids
        chat_group.members.set(member_ids)
        chat_group.save()

        group_members = []
        for mem in chat_group.members.all():
            group_members.append({
                'id': mem.id,
                'name': mem.name,
                'photo': mem.image.url,
            })
        group = {
            'id': chat_group.id,
            'name': chat_group.name,
            'members': group_members,
            'created_by': {
                'id': chat_group.created_by.id,
                'name': chat_group.created_by.name,
                'photo': chat_group.created_by.image.url,
            },
            'is_group': True,
            'create_time': str(chat_group.create_time),
        }

        event1 = {
            'name': 'chat_group_created',
            'data': group,
            'audience': member_ids
        }
        event2 = {
            'name': 'members_added_to_group',
            'data': group,
            'audience': existing_members_ids
        }
        events = [event1, event2]
        res = ws_methods.emit_event(events)
        if res == 'done':
            return {'error': '', 'data': group}
        else:
            return res

    @classmethod
    def remove_member(cls, request, params):
        member_id = params['member_id']
        group_id = params['group_id']
        chat_group = ChatGroup.objects.get(pk=group_id)
        all_member = chat_group.members.all()
        all_member_set = set(all_member)
        removed_member_set = set(AuthUser.objects.filter(id=member_id))
        remaining_members = all_member_set - removed_member_set
        chat_group.members.set(remaining_members)
        if not chat_group.members.all():
            chat_group.delete()
            return 'done'
        if chat_group.owner:
            if member_id == chat_group.owner_id:
                new_owner = all_member[0]
                chat_group.owner = new_owner
                chat_group.owner.save()
        chat_group.save()
        return 'done'

    @classmethod
    def get_details(cls, request, params):
        group_id = params['group_id']
        group_obj = ChatGroup.objects.get(pk=group_id)
        group_members = []
        for mem in group_obj.members.all():
            group_members.append({
                'id': mem.id,
                'name': mem.name,
                'photo': mem.image.url,
                'image': mem.image.url
            })
        is_owner = False
        if group_obj.owner_id == request.user.id:
            is_owner = True
        group = {
            'id': group_obj.id,
            'name': group_obj.name,
            'members': group_members,
            'is_owner': is_owner,
            'created_by': {
                'id': group_obj.created_by.id,
                'name': group_obj.created_by.name,
                'photo': group_obj.created_by.image.url,
            },
            'is_group': True,
            'show_members': True,
            'create_time': str(group_obj.create_time),
        }
        return group

    @classmethod
    def get_messages(cls, request, params):
        chat_group_id = params.get('group_id')
        offset = 0
        messages = Message.objects.filter(chat_group_id=chat_group_id).order_by('-id')[offset: offset + 20][::-1]
        messages = Message.get_processed_messages(messages, request.user.id)
        return messages


class Message(models.Model):
    sender = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    to = models.IntegerField(null=True)
    body = models.TextField()
    read_status = models.BooleanField(default=False)
    create_date = models.DateTimeField(null=True, auto_now_add=True)
    chat_group = models.ForeignKey(ChatGroup, null=True, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, null=True)

    @classmethod
    def send(cls, request, params):
        uid = request.user.id
        group_id = params.get('group_id')
        target_id = params.get('to')
        body = params['body']
        message_type = params.get('message_type')
        message = Message(sender_id=uid, body=body, create_date=datetime.now(), message_type=message_type)
        if group_id:
            message.chat_group_id = group_id
        else:
            message.to = target_id
        message.save()
        attachment_urls = []
        attachments = params.get('attachments')
        if attachments:
            for attachment in attachments:
                file_name = attachment['name']
                doc = MessageDocument(
                    message_id=message.id,
                    file_type='message',
                    name=file_name,
                    file_name=file_name,
                )

                image_data = attachment['binary']
                image_data = ws_methods.base64_str_to_file(image_data, file_name)

                doc.attachment.save(file_name, image_data, save=True)
                attachment_urls.append({
                    'name': file_name,
                    'id': doc.id,
                    'file_type': doc.extention,
                    'url': doc.attachment.url,
                })

        message_dict = message.__dict__
        message_dict['sender'] = {
            'id': message.sender.id,
            'name': message.sender.name,
            'photo': message.sender.image.url,
        }
        if message.chat_group:
            message_dict['chat_group'] = {
                'id': message.chat_group.id,
                'name': message.chat_group.name,
            }
        message_dict['attachments'] = attachment_urls
        message_dict['create_date'] = str(datetime.now())

        del message_dict['_state']
        ws_methods.stringify_fields(message_dict)
        message_dict['uuid'] = params['uuid']
        events = [
            {'name': 'chat_message_received', 'data': message_dict, 'audience': [target_id]}
        ]
        if group_id:
            events = [
                {
                    'name': 'group_chat_message_received',
                    'data': message_dict,
                    'room': {'type': 'chat_room', 'id': group_id}
                }
            ]
        res = ws_methods.emit_event(events)
        if res == 'done':
            return message_dict
        else:
            return res

    @classmethod
    def get_processed_messages(cls, messages, uid):
        ar = []
        for obj in messages:
            if obj.to and obj.sender.id != uid and not obj.read_status:
                obj.read_status = True
                obj.save()
            dict_obj = {
                'id': obj.id,
                'body': obj.body,
                'to': obj.to,
                'sender': {
                    'id': obj.sender.id,
                    'name': obj.sender.name,
                    'photo': obj.sender.image.url
                },
                'create_date': str(obj.create_date),
                'attachments': [],
                'message_type': obj.message_type
            }
            if obj.chat_group:
                status = obj.messagestatus_set.filter(message_id=obj.id, user_id=uid)
                if status:
                    status = status[0]
                    if not status.read:
                        status.read = True
                        status.save()
                dict_obj['chat_group'] = {
                    'id': obj.chat_group.id,
                    'name': obj.chat_group.name
                }
            for att in MessageDocument.objects.filter(message_id=obj.id):
                att_type = os.path.splitext(att.name)

                dict_obj['attachments'].append({
                    'name': att.name,
                    'url': att.attachment.url,
                    'id':att.id,
                    'moved':att.moved,
                    'file_type': att.extention
                })
            ar.append(dict_obj)
        return ar

    @classmethod
    def get_message_list(cls, uid, target_id, offset):
        uid = int(uid)
        target_id = int(target_id)
        user_ids = [target_id, uid]
        ar = []
        messages = Message.objects.filter(sender_id__in=user_ids, to__in=user_ids)
        if messages:
            notification_messages = messages.filter(Q(message_type='notification') & ~Q(sender_id=uid))
            general_messages = messages.filter(Q(message_type__isnull=True) & Q(sender_id__in=[uid, target_id]))
            messages = general_messages | notification_messages
            messages = messages.distinct().order_by('-id')[offset: offset + 20][::-1]
        #  & (((Q(message_type='notification') & ~Q(sender_id=uid)) | (Q(message_type__isnull=True) & Q(sender_id__in=[uid, target_id]))))
        ar = cls.get_processed_messages(messages, uid)
        return ar

    @classmethod
    def get_friend_messages(cls, request, params):
        uid = request.user.id
        target_id = params['target_id']
        data = cls.get_message_list(uid, target_id, 0)
        return data

    @classmethod
    def move_to_folder(cls, request, params):
        file_id_is = params['file_id']

        Folder = ws_methods.get_model('resources', 'Folder')
        ResourceDocument = ws_methods.get_model('resources', 'ResourceDocument')

        file = File.objects.get(pk=file_id_is)
        my_folder = Folder.objects.get(created_by_id=request.user.id, personal=True, parent_id__isnull=True)
        if not file.file_name:
            return "Invalid file name"
        doc = ResourceDocument(folder_id=my_folder.id, attachment=file.attachment, file_name=file.file_name, name=file.name, personal=True)
        doc.save()

        doc = MessageDocument.objects.get(pk=file_id_is)
        doc.moved = True
        doc.save()

        return {'data': 'File Saved Successfully' }

    @classmethod
    def move_to_other_folder(cls, request, params):
        file_id_is = params['file_id']
        folder_id  = params['folder_id']

        file = File.objects.get(pk=file_id_is)
        folder = Folder.objects.get(pk=folder_id ,created_by_id=request.user.id )
        doc = ResourceDocument(folder_id=folder.id, attachment=file.attachment, file_name=file.file_name, name=file.name, access_token='Messenger')
        doc.save()

        doc = MessageDocument.objects.get(pk=file_id_is)
        doc.moved = True
        doc.save()
        data = {"data":"File Move Successfully"}
        
        return data

    @classmethod
    def get_old_messages(cls, request, params):
        uid = request.user.id
        target_id = params['target_id']
        offset = params['offset']
        data = cls.get_message_list(uid, target_id, offset)
        return data

    @classmethod
    def mark_read_message(cls, request, params):
        uid = request.user.id
        message_id = params['message_id']
        message = Message.objects.get(pk=message_id)
        if message.to == uid:
            message.read_status = True
            message.save()
        elif message.chat_group:
            status = MessageStatus.objects.filter(message_id=message_id, user_id=uid)
            if status:
                status = status[0]
                if not status.read:
                    status.read = True
                    status.save()
        return 'done'


class MessageStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)


class MessageDocument(File):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    moved = models.BooleanField(default=False)


admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(NotificationType)
admin.site.register(MessageDocument)