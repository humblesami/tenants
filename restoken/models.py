import uuid
from django.db import models
from django.contrib.auth.models import User


class PostInfo(models.Model):
    res_app = models.CharField(max_length=128)
    res_model = models.CharField(max_length=128)
    res_id = models.IntegerField()
    def __str__(self):
        return self.res_app + '.' + self.res_model + '.' + str(self.res_id)


class PostUserToken(models.Model):
    post_info = models.ForeignKey(PostInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128)

    @classmethod
    def create_token(cls, params):
        res_app = params['res_app']
        res_model = params['res_model']
        res_id = params['res_id']
        user_id = params['user_id']
        res_app = res_app.lower()
        res_model = res_model.lower()
        post_info = PostInfo.objects.filter(res_app=res_app, res_model=res_model, res_id=res_id)
        if not post_info:
            post_info = PostInfo(res_app=res_app, res_model=res_model, res_id=res_id)
            post_info.save()
        else:
            post_info = post_info[0]
        token = uuid.uuid4().hex[:20]
        user_token = PostUserToken(post_info_id=post_info.id, user_id=user_id, token=token)
        user_token.save()
        return user_token

    @classmethod
    def validate_token(cls, token, do_not_expire=None):
        if token:
            user_token = PostUserToken.objects.filter(token=token)
            if not user_token:
                return False
            user_token1 = user_token[0]
            if not do_not_expire:
                user_token.update(token='')
            return user_token1
        else:
            return False

    @classmethod
    def validate_token_for_post(cls, token, data):
        if token:
            res_app = data['app'].lower()
            res_model = data['model'].lower()
            res_id = data['id']
            post_info = PostInfo.objects.filter(res_app=res_app, res_model=res_model, res_id=res_id)
            if not post_info:
                return 'Not token for the post ' + post_info.get('app') + '.' + post_info.get('model') + '.' + post_info.get('id')
            else:
                post_info = post_info[0]

            user_token = PostUserToken.objects.filter(token=token, post_info_id=post_info.id)
            if not user_token:
                return 'Token is expired. report_error_dev ' + str(token) +'-'+ str(post_info.id)
            user_token = user_token[0]
            return user_token
        else:
            return 'No token given to verify'