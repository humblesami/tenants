import json

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout

from dj_utils.py import HttpUtils, LogUtils
from dj_utils.dj import EmailUtils
from .models import AuthUser, DualAuth
from restoken.models import PostUserToken


class AuthMethods:

    @classmethod
    def authenticate_user(cls, request):
        params = HttpUtils.get_params(request)
        username = params.get('login')
        password = params.get('password')
        auth_user = authenticate(request, username=username, password=password)
        if auth_user and auth_user.id:
            auth_user = AuthUser.objects.filter(pk=auth_user.pk).first()
            if not auth_user:
                return {'error': 'User has not been assigned any role yet'}
        else:
            return {'error': 'Invalid credentials'}
        auth_type = (auth_user.two_factor_auth or '').lower()
        if auth_type and not settings.IS_LOCALHOST:
            res = cls.send_verification_code(auth_user, auth_type)
            return res
        if auth_user and auth_user.id:
            return cls.acknowledge_user(request, auth_user)
        else:
            return 'Invalid credentials'

    @classmethod
    def send_verification_code(cls, auth_user, auth_type):
        address_to_send_code = auth_user.email
        if auth_type == 'phone':
            if not auth_user.mobile_phone:
                return {'error': 'User phone does not exist to send code, please ask admin to set it for you'}
            address_to_send_code = auth_user.mobile_phone
        else:
            if not auth_user.email:
                return {'error': 'User email does not exist to send code, please ask admin to set it for you'}
        auth_data = 'auth_type=' + auth_type + '&address=' + address_to_send_code
        url = settings.AUTH_SERVER_URL + '/auth-code/generate?' + auth_data
        res = HttpUtils.http_get(url)
        try:
            res = json.loads(res)
        except:
            return res
        res['address'] = address_to_send_code[:2] + '****' + address_to_send_code[-2:]
        res['auth_type'] = auth_type
        dual_auth = DualAuth(
            user_id=auth_user.pk,
            uuid=res['uuid']
        )
        dual_auth.save()
        return res

    @classmethod
    def verify_code(cls, request):
        params = HttpUtils.get_params(request)
        auth_code = params.get('auth_code')
        uuid = params.get('uuid')
        if not uuid or not auth_code:
            return {'error': 'Please provide code and uuid'}
        url = settings.AUTH_SERVER_URL + '/auth-code/verify?code=' + auth_code + '&uuid=' + uuid
        res = HttpUtils.http_get(url)
        if res != 'ok':
            return res
        dual_auth = DualAuth.objects.get(uuid=uuid)
        user = dual_auth.user
        return user

    @classmethod
    def acknowledge_user(cls, request, user):
        login(request, user)
        token = Token.objects.filter(user=user)
        if token:
            token = token[0]
        token.delete()
        token = Token.objects.create(user=user)
        user_groups = list(user.groups.all().values())
        user_data = {
            'username': user.username, 'name': user.full_name(),
            'id': user.id, 'token': token.key, 'groups': user_groups
        }
        try:
            user_data['photo'] = user.authuser.image.url
            user_data['user_photo'] = user_data['photo']
        except:
            pass
        request.user = user
        return user_data


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
    def logout_user(cls, request, params):
        logout(request)
        return {'error': '', 'data': 'ok'}


    @classmethod
    def register_user(cls, request):
        return {}


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
        user_token = PostUserToken.validate_token(token, 1)
        if user_token:
            user = user_token.user
            request.user = user
            user.set_password(password)
            user.email_verified = True
            user.save()
            return 'done'
        else:
            if request.user.id:
                user = request.user
                user.set_password(password)
                user.save()
                return 'done'
            else:
                return 'Something went Wrong'


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
                'url': settings.server_base_url + '/user/reset-password/'
            }
            thread_data['template_name'] = 'user/reset_password.html'
            thread_data['token_required'] = 1
            thread_data['post_info'] = {
                'res_app': params.get('app'),
                'res_model': 'Profile',
                'res_id': user.id
            }
            EmailUtils.send_mail_data(thread_data)
            return 'done'
        except:
            res = LogUtils.get_error_message()
            return res

    @classmethod
    def password_reset_on_creation_email(cls, user_obj, random_password):
        try:
            if not user_obj.email:
                return 'User email not exists in system'

            thread_data = {
                'subject': 'Password Rest',
                'audience': [user_obj.id],
                'template_data': {
                    'url': settings.server_base_url + '/user/reset-password/',
                    'password': random_password
                },
                'template_name': 'user/user_creation_password_reset.html',
                'token_required': 1,
                'post_info': {
                    'res_app': 'authsignup',
                    'res_model': 'AuthUser',
                    'res_id': user_obj.id
                }
            }

            EmailUtils.send_mail_data(thread_data)
            return 'done'
        except:
            res = LogUtils.get_error_message()
            return res
