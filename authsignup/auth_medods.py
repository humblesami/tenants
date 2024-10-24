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


    @classmethod
    def do_login(cls, request, user, name):
        token = Token.objects.filter(user=user)
        if token:
            token = token[0]

        login(request, user)
        token.delete()
        token = Token.objects.create(user=user)

        user_groups = list(user.groups.all().values())
        user_data = {'username': user.username, 'name': name, 'id': user.id, 'token': token.key, 'groups': user_groups}
        try:
            user_data['photo'] = user.authuser.image.url
            user_data['user_photo'] = user_data['photo']
        except:
            pass
        request.user = user
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
                auth_type = auth_user.two_factor_auth
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
        url = settings.AUTH_SERVER_URL + '/auth-code/generate?' + auth_data
        res = HttpUtils.http_request(url)
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
        url = settings.AUTH_SERVER_URL + '/auth-code/verify?code=' + auth_code + '&uuid=' + uuid
        res = HttpUtils.http_request(url)
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