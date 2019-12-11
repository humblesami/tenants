import io
import base64

from django.db import models
from django.db.models import UniqueConstraint
from django.core.files.base import ContentFile
from django.core.files import File as DjangoFile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group as group_model, UserManager


from mainapp import ws_methods
from documents.file import File
from authsignup.models import AuthUser, LoginEntry
from meetings.model_files.committee import Committee
from chat.models import Message, UserNotification, MessageStatus

GENDER_CHOICES = (
    (1, _("Male")),
    (2, _("Female")),
    (3, _("Other")),
    (4, _("I decline to answer"))
)
MARITAL_CHOICES = (
    (1, _("Single")),
    (2, _("Married")),
    (3, _("Widower")),
    (4, _("Divorced"))
)
YES_NO_CHOICES = (
    (1, _("Yes")),
    (2, _("No")),
    (3, _("I decline to answer"))
)
ETHINICITY_CHOICES = (
    (1, _("Hispanic or Latino")),
    (2, _("American Indian or Alaskan Native")),
    (3, _("Asian")),
    (4, _("Native Hawaiian or Other Native Pacific Islander")),
    (5, _("Black or African American")),
    (6, _("White")),
    (7, _("Two or more races")),
    (8, _("I decline to answer"))
)

class Profile(AuthUser):
    class Meta:
        verbose_name_plural = "BoardSheet  Users"
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nick_name = models.CharField(max_length=30, blank=True)
    job_title = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=30, blank=True)
    work_phone = models.CharField(max_length=30, blank=True)

    website = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    ethnicity = models.IntegerField(choices=ETHINICITY_CHOICES, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True)
    veteran = models.IntegerField(choices=YES_NO_CHOICES, blank=True, null=True)
    disability = models.IntegerField(choices=YES_NO_CHOICES, blank=True, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)
    board_joining_date = models.DateField('board joining date', blank=True, null=True)
    admin_first_name = models.CharField(max_length=30, blank=True, null=True)
    admin_last_name = models.CharField(max_length=30, blank=True, null=True)
    admin_nick_name = models.CharField(max_length=30, blank=True, null=True)
    admin_cell_phone = models.CharField(max_length=30, blank=True, null=True)
    admin_email = models.CharField(max_length=30, blank=True, null=True)
    admin_work_phone = models.CharField(max_length=30, blank=True, null=True)
    admin_fax = models.CharField(max_length=30, blank=True, null=True)
    admin_image = models.ImageField(upload_to='profile/', default='profile/default.png', null=True)
    mail_to_assistant = models.BooleanField(blank=True, null=True)
    term_start_date = models.DateField(blank=True, null=True)
    term_end_date = models.DateField(blank=True, null=True)
    signature_data = models.BinaryField(default=b'', null=True, blank=True)
    resume = models.OneToOneField(File, null=True, blank=True, on_delete=models.SET_NULL)
    # user_type = models.CharField(max_length=50)

    UniqueConstraint(fields=['email'], name='unique_email')

    def __str__(self):
        return self.fullname()

    def save(self, *args, **kwargs):
        creating = False
        if not self.pk:
            creating = True
            self.is_staff = True
            if self.email:
                self.username = self.email
        super(Profile, self).save(*args, **kwargs)
        if creating:
            user_data = {
                'id': self.pk,
                'photo': self.image.url,
                'name': self.fullname()
            }
            events = [
                {'name': 'new_friend', 'data': user_data, 'audience': ['all_online']}
            ]
            ws_methods.emit_event(events)

    def is_admin(self):
        admin = False
        if self.groups.filter(name__in=['Admin']):
            admin = True
        return admin

    @classmethod
    def get_records(cls, request, params):
        group = params.get('type')
        profiles = []
        kw = params.get('kw')
        if kw:
            profiles = ws_methods.search_db({'kw': kw, 'search_models': {'meetings': ['Profile']}})
        else:
            profiles = Profile.objects.all().order_by('-pk')
            
        if group:
            profiles = profiles.filter(groups__name__iexact=group).order_by('-pk')
        
        total_cnt = profiles.count()
        offset = params.get('offset')
        limit = params.get('limit')
        profiles = list(profiles)
        if limit:
            profiles = profiles[offset: offset + int(limit)]
        profiles = ws_methods.get_user_info(profiles)
        count = len(profiles)
        profiles_json = {'records': profiles, 'total': total_cnt, 'count': count}
        return profiles_json

    @classmethod
    def get_personal_info(cls, request, params):
        profile_obj = params['profile_obj']
        profile = ws_methods.obj_to_dict(profile_obj, fields=[
            'id',
            'first_name',
            'last_name',
            'mobile_phone',
            'email',
            'birth_date',
            'location',
            'email_verified',
            'mobile_verified',
            'image'
        ])
        resume = profile_obj.resume
        if resume:
            profile['resume'] = {'id': resume.id}
        profile['signature_data'] = profile_obj.signature_data.decode()
        profile['two_factor_auth'] = {
            'id': profile_obj.two_factor_auth,
            'name': profile_obj.get_two_factor_auth_display()
        }
        return profile

    @classmethod
    def get_work_info(cls, request, params):
        profile_obj = params['profile_obj']
        profile = ws_methods.obj_to_dict(profile_obj, fields=[
            'company',
            'job_title',
            'department',
            'work_phone',
            'fax',
            'website',
        ])

        return profile

    @classmethod
    def get_board_info(cls, request, params):
        profile_obj = params['profile_obj']
        profile = ws_methods.obj_to_dict(profile_obj, fields=[
                    'board_joining_date',
                    'term_start_date',
                    'term_end_date'
                ],
                related={
                 'committees': {'fields': ['id', 'name']}
                })
        return profile

    def get_assistant_name(self):
        a_full_name = ''
        if self.admin_first_name:
            a_full_name = self.admin_first_name
        if self.admin_last_name and self.admin_first_name:
            a_full_name += ' ' + self.admin_last_name
        elif self.admin_last_name:
            a_full_name = self.admin_last_name
        return a_full_name

    @classmethod
    def get_admin_assistant_info(cls, request, params):
        profile_obj = params['profile_obj']
        profile = ws_methods.obj_to_dict(profile_obj, fields=[
            'admin_first_name',
            'admin_last_name',
            'admin_cell_phone',
            'admin_email',
            'admin_work_phone',
            'admin_fax',
            'admin_image',
            'mail_to_assistant'])
        profile['admin_full_name'] = profile_obj.get_assistant_name()
        return profile

    @classmethod
    def get_update_profile_details(cls, request, params):
        field_group = params['field_group']
        user_id = params.get('id')
        if not user_id:
            user_id = request.user.id
        group = params.get('type')
        profile_obj = Profile.objects.get(pk=user_id)
        profile = {}
        choice_fields = {
            'gender': [{'id': 0, 'name': ''}],
            'disability': [{'id': 0, 'name': ''}],
            'ethnicity': [{'id': 0, 'name': ''}],
            'veteran': [{'id': 0, 'name': ''}],
            'committees': [{'id': 0, 'name': ''}],
            'two_factor_auth': [{'id': 0, 'name': ''}],
            'groups': [{'id': 0, 'name': ''}]
        }
        param = {}
        param['profile_obj'] = profile_obj
        if field_group == 'personal':
            profile = cls.get_personal_info(request, param)
            choice_fields['two_factor_auth'] = ws_methods.choices_to_list(profile_obj._meta.get_field('two_factor_auth').choices)
        elif field_group == 'bio':
            profile = ws_methods.obj_to_dict(profile_obj, fields=['bio'],related={'groups': {'fields': ['id', 'name']}})
        elif field_group == 'work':
            profile = cls.get_work_info(request, param)
        elif field_group == 'board':
            profile = cls.get_board_info(request, param)
            choice_fields['committees'] = list(Committee.objects.values('id', 'name'))
            choice_fields['groups'] = list(group_model.objects.all().values('id', 'name'))
        elif field_group == 'diversity':
            choice_fields['gender'] = ws_methods.choices_to_list(profile_obj._meta.get_field('gender').choices)
            choice_fields['disability'] = ws_methods.choices_to_list(profile_obj._meta.get_field('disability').choices)
            choice_fields['ethnicity'] = ws_methods.choices_to_list(profile_obj._meta.get_field('ethnicity').choices)
            choice_fields['veteran'] = ws_methods.choices_to_list(profile_obj._meta.get_field('veteran').choices)
        elif field_group == 'administrative':
            profile = cls.get_admin_assistant_info(request, param)
        profile['groups'] = []
        groups = profile_obj.groups.all().values('id', 'name')
        for group in groups:
            profile['groups'].append(group)
        profile['name'] = profile_obj.fullname()
        profile['disability'] = {
            'id': profile_obj.disability,
            'name': profile_obj.get_disability_display()
        }
        profile['ethnicity'] = {
            'id': profile_obj.ethnicity,
            'name': profile_obj.get_ethnicity_display()
        }
        profile['gender'] = {
            'id': profile_obj.gender,
            'name': profile_obj.get_gender_display()
        }
        profile['veteran'] = {
            'id': profile_obj.veteran,
            'name': profile_obj.get_veteran_display()
        }
        profile['two_factor_auth'] = {
            'id': profile_obj.two_factor_auth,
            'name': profile_obj.get_two_factor_auth_display()
        }
        if profile['groups']:
            profile['group'] = profile['groups'][0]['name']
        data = {"profile": profile, "next": 0, "prev": 0, 'choice_fields': choice_fields}
        return data

    @classmethod
    def get_details(cls, request, params):
        user_id = params.get('id')
        if not user_id:
            user_id = request.user.id
        profile_orm = None
        if user_id == 'new':
            profile_orm = Profile.objects.filter(created_by_id=request.user.id).last()
            if profile_orm:
                user_id = profile_orm.id
        else:
            profile_orm = Profile.objects.get(pk=user_id)

        if not profile_orm:
            return 'No role assigned yet'
        else:
            assistant_name = ''
            try:
                assistant_name = profile_orm.get_assistant_name()
            except:
                pass
        profile = ws_methods.obj_to_dict(
            profile_orm,
            fields=[
                'id', 'name', 'username', 'first_name', 'last_name', 'email', 'image', 'bio', 'location', 'birth_date',
                'nick_name', 'company', 'job_title', 'department',
                'work_phone', 'mobile_phone', 'website', 'fax', 'ethnicity', 'gender', 'veteran',
                'disability', 'board_joining_date', 'admin_first_name', 'admin_last_name', 'admin_nick_name',
                'admin_cell_phone', 'admin_email', 'admin_work_phone', 'admin_fax', 'admin_image', 'mail_to_assistant',
                'term_start_date', 'term_end_date', 'date_joined', 'groups', 'email_verified', 'mobile_verified'
            ],
            related={
                'committees': {'fields': ['id', 'name']},
                'groups': {'fields': ['id', 'name']}
            }
        )
        if not profile['name']:
            profile['name'] = profile_orm.fullname()
        # profile['date_joined'] = str(profile['date_joined'])
        profile['disability'] = {
            'id': profile_orm.disability,
            'name': profile_orm.get_disability_display()
        }
        profile['ethnicity'] = {
            'id': profile_orm.ethnicity,
            'name': profile_orm.get_ethnicity_display()
        }
        profile['gender'] = {
            'id': profile_orm.gender,
            'name': profile_orm.get_gender_display()
        }
        profile['veteran'] = {
            'id': profile_orm.veteran,
            'name': profile_orm.get_veteran_display()
        }
        profile['two_factor_auth'] = {
            'id': profile_orm.two_factor_auth,
            'name': profile_orm.get_two_factor_auth_display()
        }
        if profile_orm.signature_data:
            profile['signature_data'] = profile_orm.signature_data.decode()
        if profile['groups']:
            profile['group'] = profile['groups'][0]['name']
        profile['admin_full_name'] = assistant_name
        resume = profile_orm.resume
        if resume:
            profile['resume'] = {'id': resume.id}
        gender = ws_methods.choices_to_list(profile_orm._meta.get_field('gender').choices)
        disability = ws_methods.choices_to_list(profile_orm._meta.get_field('disability').choices)
        ethnicity = ws_methods.choices_to_list(profile_orm._meta.get_field('ethnicity').choices)
        veteran = ws_methods.choices_to_list(profile_orm._meta.get_field('veteran').choices)
        two_factor_auth = ws_methods.choices_to_list(profile_orm._meta.get_field('two_factor_auth').choices)
        committees = list(Committee.objects.values('id', 'name'))
        groups = list(group_model.objects.all().values('id', 'name'))
        choice_fields = {
            'gender': gender,
            'disability': disability,
            'ethnicity': ethnicity,
            'veteran': veteran,
            'committees': committees,
            'two_factor_auth': two_factor_auth,
            'groups': groups
        }
        profile['login_info'] = LoginEntry.get_last_login_info(profile_orm.id)
        data = {"profile": profile, "next": 0, "prev": 0, 'choice_fields': choice_fields}
        return data

    @classmethod
    def get_profile_summary(cls, request, params):
        user_id = params['user_id']
        profile_obj = Profile.objects.get(pk=user_id)
        profile = ws_methods.obj_to_dict(
            profile_obj,
            fields=['id', 'name', 'first_name', 'last_name', 'image', 'mobile_phone','company', 'email']
        )
        profile['groups'] = []
        groups = profile_obj.groups.all().values('id', 'name')
        for group in groups:
            profile['groups'].append(group)

        profile['photo'] = profile['image']
        return profile

    @classmethod
    def update_profile(cls, request, params):
        request_user = request.user
        request_user = Profile.objects.get(pk=request_user.id)
        if not request_user.is_admin():
            params.pop('committees', None)
            params.pop('groups', None)
        user_id = params.get('user_id')
        if not user_id:
            user_id = request.user.id
        profile = Profile.objects.get(pk=user_id)
        for key in params:
            if key != 'committees' and key != 'signature_data' and key != ' image' and key != ' admin_image' and key != 'resume' and key != 'groups':
                if params[key] == '' and not profile._meta._forward_fields_map[key].max_length:
                    params[key] = None
                setattr(profile, key, params[key])
        committees = params.get('committees')
        if committees:
            if committees != 'removed_all':
                committee_ids = []
                for committee in committees:
                    committee_ids.append(committee['id'])

                all_committees = Committee.objects.filter(pk__in=committee_ids)
                current_committees = profile.committees.all()
                new_committees = set(all_committees) - set(current_committees)
                removed_committees = set(current_committees) - set(all_committees)
                for committee in new_committees:
                    committee.users.add(user_id)
                    committee.save()

                for committee in removed_committees:
                    committee.users.remove(user_id)
                    committee.save()
            else:
                current_committees = profile.committees.all()
                for committee in current_committees:
                    committee.users.remove(user_id)
                    committee.save()

        if params.get('resume'):
            image_data = params['resume']

            format, imgstr = image_data.split(';base64,')
            binary_data = io.BytesIO(base64.b64decode(imgstr))
            jango_file = DjangoFile(binary_data)

            file_name = ''
            resume_file = profile.resume  # File.objects.filter(user_id=user_id)
            if not resume_file:
                file_name = 'resume_' + str(user_id) + '.pdf'
            else:
                file_name = resume_file.name
            resume_file = File(name=file_name, file_type='resume')
            resume_file.attachment.save(file_name, jango_file)
            resume_file.save()
            profile.resume = resume_file
        elif 'resume' in params:
            profile.resume = None
            profile.save();

        if params.get('image'):
            image_data = params['image']
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr))
            file_name = 'image_' + str(user_id) + '.' + ext
            profile.image.save(file_name, data, save=True)

        if params.get('admin_image'):
            image_data = params['admin_image']
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr))
            file_name = 'admin_image_' + str(user_id) + '.' + ext
            profile.admin_image.save(file_name, data, save=True)

        if 'groups' in params:
            groups = profile.groups.all()
            for group in groups:
                group.user_set.remove(user_id)
                group.save()
            groups = params.get('groups')
            if groups:
                for group in groups:
                    profile.groups.add(group['id'])
                    profile.save()

        profile.save()
        data = {
            'id': profile.id,
            'name': profile.name,
            'photo': profile.image.url,
            'groups': list(profile.groups.all().values('id', 'name')),
            'username': profile.username
        }
        return {'profile_data': data}

    @classmethod
    def save_signature(cls, request, params):
        user_id = params.get('user_id')
        if not user_id:
            user_id = request.user.id
        profile = Profile.objects.get(pk=user_id)
        signature_data = params['signature_data']
        signature_data = signature_data.encode()
        # signature_data = base64.encodebytes(signature_data)
        profile.signature_data = signature_data
        profile.save()
        return 'done'

    def delete(self, using=None, keep_parents=False):
        uid = self.pk
        super(Profile, self).delete()
        events = [
            {'name': 'friend_removed', 'data': uid, 'audience': ['all_online']}
        ]
        ws_methods.emit_event(events)

    @classmethod
    def get_all_users(cls, request, params):
        users = None
        kw = params.get('kw')
        if kw:
            users = ws_methods.search_db({'kw': kw, 'search_models': {'meetings': ['Profile']}})

        else:
            users = Profile.objects.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'image': user.image.url
            })
        data = {
            'users': user_list,
            'total': len(user_list)
        }
        return data

    @classmethod
    def verify_chat_user(cls, request, params):
        data = {
            'friends': [],
            'friendIds': [],
            'notifications': [],
            'unseen': 0,
            'committees': [],
            'meetings': [],
            'user': {
                'id': request.user.id,
                'name': 'Anonymous',
                'photo': 'https://theareligroup.com/wp-content/uploads/2016/03/user-experiance-icon.png',
            }
        }
        try:
            uid = params['id']
            uid = int(uid)
            chat_users = Profile.objects.exclude(pk=uid).values('id', 'name', 'image', 'groups')
            chat_users = list(chat_users)
            unseen_messages = 0
            friend_ids = []
            committees = []
            meetings = []
            for friend in chat_users:
                unseen = len(Message.objects.filter(sender_id=friend['id'], read_status=False, to=uid))
                friend['unseen'] = unseen
                unseen_messages += unseen
                friend_ids.append(friend['id'])
                friend['unseen'] = unseen
                friend['photo'] = '/media/' + friend['image']

            profile_object = Profile.objects.filter(pk=uid)
            res = False
            if not profile_object:
                return 'Profile not created yet'
            else:
                profile_object = profile_object[0]
                res = None
                if not profile_object.groups.all():
                    return 'No role assigned yet to user'
            if res != 'done':
                if res:
                    data['message'] = {'error': res}
                else:
                    data['message'] = {'error': 'Error in group creation'}
            req_user = {
                'id': uid,
                'name': profile_object.name,
                'photo': profile_object.image.url,
                'groups': list(profile_object.groups.all().values('id', 'name'))
            }
            committee_objects = profile_object.committees.all()
            for obj in committee_objects:
                committees.append({'id': obj.id, 'name': obj.name})
            meeting_objects = profile_object.meetings.all()
            for obj in meeting_objects:
                meetings.append({'id': obj.id, 'name': obj.name})
            for com in committee_objects:
                committees.append({'id': com.id, 'name': com.name})
            notifications = UserNotification.get_my_notifications(request, False)
            chat_groups = profile_object.chat_groups.filter(active=True)
            chat_groups_list = []
            for obj in chat_groups:
                unseen = len(MessageStatus.objects.filter(message__chat_group_id=obj.id, read=False))
                is_owner = False
                if obj.owner_id == request.user.id:
                    is_owner = True
                chat_group = {
                    'id': obj.id, 'name': obj.name, 'unseen': unseen,
                    'photo': '/static/assets/images/group.jpeg',
                    'members': [],
                    'is_owner': is_owner,
                    'created_by': {
                        'id': obj.created_by.id,
                        'name': obj.created_by.name,
                        'photo': obj.created_by.image.url,
                    },
                    'is_group': True
                }
                chat_groups_list.append(chat_group)
            data = {
                'friends': chat_users,
                'friendIds': friend_ids,
                'notifications': notifications,
                'unseen': unseen_messages,
                'user': req_user,
                'committees': committees,
                'meetings': meetings,
                'chat_groups': chat_groups_list
            }
        except:
            ws_methods.produce_exception()
        return data


class ManagerDirector(UserManager):
    def get_queryset(self):
        return super(ManagerDirector, self).get_queryset().filter(groups__name__in=['Director'])


class ManagerAdmin(UserManager):
    def get_queryset(self):
        return super(ManagerAdmin, self).get_queryset().filter(groups__name__in=['Admin'])


class ManagerStaff(UserManager):
    def get_queryset(self):
        return super(ManagerStaff, self).get_queryset().filter(groups__name__in=['Staff'])