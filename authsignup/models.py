import os
import uuid

from .models_login import *
from restoken.models import PostUserToken
from mainapp.models import CustomModel
from mainapp.settings import AUTH_SERVER_URL, server_base_url

from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User as user_model
from django.contrib.auth import authenticate, login, logout


TWO_FACTOR_CHOICES = (
    (1, _("Email")),
    (2, _("Phone"))
)


class DualAuth(models.Model):
    uuid = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


# Create your models here.
class AuthUser(user_model, CustomModel):
    name = models.CharField(max_length=200, default='', blank=True)
    image = models.ImageField(upload_to='profile/', default='profile/default.png', null=True)
    two_factor_auth = models.IntegerField(choices=TWO_FACTOR_CHOICES, blank=True, null=True)
    email_verified = models.BooleanField(null=True, default=False)
    mobile_verified = models.BooleanField(null=True, default=False)
    mobile_phone = models.CharField(max_length=30, blank=True)
    image_updated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        creating = False
        if self.pk:
            creating = True
        super(AuthUser, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     creating = False
    #     if self.two_factor_auth and self.two_factor_auth == 2 and not self.mobile_verified:
    #         return
    #     profile_obj = AuthUser.objects.filter(pk=self.pk)
    #     if not profile_obj:
    #         creating = True
    #         self.is_staff = True
    #         if self.email and not self.username:
    #             self.username = self.email
    #         self.image = ws_methods.generate_default_image(self.fullname())
    #     self.name = self.fullname()
    #     if profile_obj:
    #         profile_obj = profile_obj[0]
    #         if self.image != profile_obj.image:
    #             self.image_updated = True
    #         if not self.image_updated:
    #             if self.name != profile_obj.name:
    #                 curr_dir = os.path.dirname(__file__) + '/images'
    #                 try:
    #                     os.remove(curr_dir + profile_obj.image.url)
    #                 except:
    #                     pass
    #                 self.image = ws_methods.generate_default_image(self.name)
    #
    #     random_password = None
    #     if self.password and len(self.password) <= 15:
    #         random_password = self.password
    #     super(AuthUser, self).save(*args, **kwargs)
    #     if creating:
    #         if not self.is_superuser:
    #             if not random_password:
    #                 random_password = uuid.uuid4().hex[:8]
    #             self.password_reset_on_creation_email(random_password)
    #     if random_password:
    #         self.set_password(random_password)
    #         super(AuthUser, self).save(*args, **kwargs)

    def fullname(self):
        user = self
        name = False
        if user.first_name:
            name = user.first_name
        if user.last_name:
            name += ' ' + user.last_name
        if not name:
            if not self.name:
                name = user.username
            else:
                name = self.name
        return name

    def password_reset_on_creation_email(self, random_password):
        try:
            if not self.email:
                return 'User email not exists in system'

            thread_data = {}
            thread_data['subject'] = 'Password Rest'
            thread_data['audience'] = [self.id]
            thread_data['template_data'] = {
                'url': server_base_url + '/user/reset-password/',
                'password': random_password
            }
            thread_data['template_name'] = 'user/user_creation_password_reset.html'
            thread_data['token_required'] = 1
            thread_data['post_info'] = {
                'res_app': 'authsignup',
                'res_model': 'AuthUser',
                'res_id': self.id
            }
            ws_methods.send_email_on_creation(thread_data)
            return 'done'
        except:
            res = ws_methods.get_error_message()
            return res


    @classmethod
    def do_login(cls, request, user, name, referer_address):
        login(request, user)
        token = Token.objects.filter(user=user)
        if token:
            token = token[0]

        if 'localhost' in referer_address:
            if not token:
                token = Token.objects.create(user=user)
        else:
            token.delete()
            token = Token.objects.create(user=user)

        user_groups = list(user.groups.all().values())
        user_data = {'username': user.username, 'name': name, 'id': user.id, 'token': token.key, 'groups':user_groups }
        try:
            user_data['photo'] = user.authuser.image.url
            user_data['user_photo'] = user_data['photo']
        except:
            pass        
        """ Creating Peronsl Folder if not exists """
        folder_model = ws_methods.get_model('resources', 'Folder')
        method_to_call =  getattr(folder_model, 'create_personal_folder')
        request.user = user
        method_to_call(folder_model, request, {})
        """Deleting All Temp Files"""
        ws_methods.delete_all_temp_files(request, user.id)
        return user_data

    @classmethod
    def login_user(cls, request, params):
        username = params.get('login')
        password = params.get('password')
        auth_code = params.get('auth_code')
        referer_address = request.META.get('HTTP_REFERER') or ''
        auth_user = None
        if auth_code:
            uuid = params.get('uuid')
            res = cls.verify_code(uuid, auth_code)
            if type(res) is str:
                return res
            auth_user = res
        else:
            user = authenticate(request, username=username, password=password)
            if user and user.id:
                auth_user = AuthUser.objects.filter(pk=user.id).first()
                if not auth_user:
                    return 'User has not been assigned any role yet'
            else:
                return 'Invalid credentials'

            auth_type = None
            if auth_user.two_factor_auth:
                auth_type = auth_user.get_two_factor_auth_display()
            if auth_type:
                if not referer_address.endswith('localhost:4200/'):
                    auth_type = auth_type.lower()
                    address_to_send_code = ''
                    if auth_type == 'phone':
                        if not user.mobile_phone:
                            return 'User phone does not exist to send code, please ask admin to set it for you'
                        address_to_send_code = user.mobile_phone
                    else:
                        if not user.email:
                            return 'User email does not exist to send code, please ask admin to set it for you'
                        address_to_send_code = user.email
                    res = cls.send_verification_code(auth_type, address_to_send_code, user.id)
                    return res
        if user and user.id:
            name = ''
            try:
                name = user.fullname()
            except:
                if user.first_name:
                    name = user.first_name
                if user.last_name:
                    name += user.last_name
                if not name:
                    name = user.username
            return cls.do_login(request, user, name, referer_address)
        else:
            return {'error': 'Invalid credentials'}

    @classmethod
    def send_verification_code(cls, auth_type, address_to_send_code, user_id):
        if not address_to_send_code:
            return 'No address given to send code'
        auth_data = 'auth_type=' + auth_type + '&address=' + address_to_send_code
        url = AUTH_SERVER_URL + '/auth-code/generate?' + auth_data
        res = ws_methods.http_request(url)
        try:
            res = json.loads(res)
        except:
            return res
        res['address'] = address_to_send_code[:2] + '****' + address_to_send_code[-2:]
        res['auth_type'] = auth_type
        dual_auth = DualAuth(
            user_id=user_id,
            uuid=res['uuid']
        )
        dual_auth.save()
        return res

    @classmethod
    def verify_code(cls, uuid, auth_code):
        if not uuid:
            return {'error': 'No request id found'}
        url = AUTH_SERVER_URL + '/auth-code/verify?code=' + auth_code + '&uuid=' + uuid
        res = ws_methods.http_request(url)
        if res != 'ok':
            return res
        dual_auth = DualAuth.objects.get(uuid=uuid)
        user = dual_auth.user
        return user

    @classmethod
    def authenticate_mobile(cls, request, params):
        auth_code = params['verification_code']
        uuid = params['uuid']
        res = cls.verify_code(uuid, auth_code)
        if type(res) is str:
            return res
        user = AuthUser.objects.get(pk=res.id)
        if user:
            user.mobile_verified = True
        return 'done'

    @classmethod
    def send_mobile_verfication_code(cls, request, params):
        user = request.user
        user = AuthUser.objects.get(pk=user.id)
        mobile_phone = params['mobile_phone']
        if mobile_phone:
            user.mobile_phone = mobile_phone
            user.save()
            auth_type = 'phone'
            auth_type = auth_type.lower()
            address_to_send_code = mobile_phone
            user_id = user.id
            res = cls.send_verification_code(auth_type, address_to_send_code, user_id)
            return res
        else:
            return 'Please provide mobile number.'

    @classmethod
    def logout_user(cls, request, params):
        ws_methods.delete_all_temp_files(request, request.user.id)
        logout(request)
        return {'error': '', 'data': 'ok'}

    @classmethod
    def change_password(cls, request, params):
        old_password = params['old']
        new_password = params['new']

        username = request.user.username
        user = authenticate(request, username=username, password=old_password)
        if user and user.id:
            user = request.user
            user.set_password(new_password)
            user.save()
            return 'done'
        else:
            return 'Wrong old password'

    @classmethod
    def set_user_password(cls, request, params):
        password = params['password']
        token = params['token']
        user_token = PostUserToken.validate_token(token,1)
        if user_token:
            user = user_token.user
            request.user = user
            user.set_password(password)
            user.email_verfied = True
            user.save()
            return 'done'
        else:
            if request.user.id:
                user = request.user
                user.set_password(password)
                user.save()
                return 'done'
            else:
                return 'Something Wents Wrong'

    @classmethod
    def reset_password(cls, request, params):
        try:
            user = User.objects.filter(email=params['email'])
            if not user:
                return 'User email not exists in system'
            else:
                user = user[0]
            thread_data = {}
            thread_data['subject'] = 'Password Rest'
            thread_data['audience'] = [user.id]
            thread_data['template_data'] = {
                'url': server_base_url + '/user/reset-password/'
            }
            thread_data['template_name'] = 'user/reset_password.html'
            thread_data['token_required'] = 1
            thread_data['post_info'] = {
                'res_app': 'meetings',
                'res_model': 'Profile',
                'res_id': user.id
            }
            ws_methods.send_email_on_creation(thread_data)
            return 'done'
        except:
            res = ws_methods.get_error_message()
            return res