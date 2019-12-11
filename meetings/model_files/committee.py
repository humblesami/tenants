from django.db import models
from mainapp import ws_methods
from mainapp.models import CustomModel
from django.db.models.signals import m2m_changed
from django_currentuser.middleware import get_current_user
from mainapp.settings import server_base_url


class Committee(CustomModel):
    name = models.CharField(max_length=150)
    users = models.ManyToManyField('meetings.Profile', blank=True, related_name="committees")
    description = models.TextField(max_length=500, default='', blank=True)
    allUser = models.BooleanField('All Users', default=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_detail(cls, request, params):
        comm_id = params['id']
        user_id = request.user.id
        committee_orm = None
        if comm_id == 'new':
            if not user_id:
                return 'Invalid committee id'
            committee_orm = Committee.objects.filter(created_by_id=user_id).last()
            if committee_orm:
                comm_id = committee_orm.id
        else:
            committee_orm = Committee.objects.filter(pk=comm_id)[0]
        committee = ws_methods.obj_to_dict(
            committee_orm,
            fields=['id', 'name', 'description']
        )
        if committee:
            kw = params.get('kw')
            if kw:
                committee_users = ws_methods.search_db({'kw': kw, 'search_models': {'meetings': ['Profile']}})
                committee_users = ws_methods.get_user_info(committee_users)
            else:
                committee_users = ws_methods.get_user_info(committee_orm.users.filter(groups__name__in=['Admin','Staff','Director']).distinct())
            
            total_cnt = len(committee_users)
            offset = params.get('offset')
            limit = params.get('limit')
            committee_users = list(committee_users)
            if limit:
                committee_users = committee_users[offset: offset + int(limit)]
            current_cnt = len(committee_users)
            committee['users'] = committee_users

            data = {"committee": committee, "next": 0, "prev": 0, "count": current_cnt,"total": total_cnt}
            return data
        else:
            return {'error': 'Committee Not Found against Specific Details'}

    @classmethod
    def get_records(cls, request, params):
        kw = params.get('kw')
        committees_orm = []
        if kw:
            committees_orm = ws_methods.search_db({'kw': kw, 'search_models': {'meetings': ['Committee']}})
        else:
            committees_orm = Committee.objects.filter().order_by('-pk')
        total_cnt = committees_orm.count()
        offset = params.get('offset')
        limit = params.get('limit')
        committees_orm = list(committees_orm)
        if limit:
            committees_orm = committees_orm[offset: offset + int(limit)]
        committees = ws_methods.queryset_to_list(
            committees_orm,
            fields=['id', 'name', 'description'],
            related={
                'users': {'fields': ['id', 'username', 'image']}
            }
        )
        count = len(committees)
        data = {'records':committees, 'total': total_cnt, 'count': count}
        return data


    def committee_email(self, audience, action=None):
        template_data = {
            'id': self.id,
            'name': self.name,
            'server_base_url': server_base_url
        }
        post_info = {}
        post_info['res_app'] = self._meta.app_label
        post_info['res_model'] = self._meta.model_name
        post_info['res_id'] = self.id
        if action:
            template_name = 'committee/removed_from_committee_email.html'
            token_required = False
        else:
            template_name = 'committee/added_to_committee_email.html'
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


def save_committee_users(sender, instance, action, pk_set, **kwargs):
    # if action == 'post_remove':
    #     removed_respondents = list(pk_set)
    #     instance.committee_email(removed_respondents, 'removed')
    if action == "post_add":
        new_added_respondets = list(pk_set)
        try:
            new_added_respondets.remove(get_current_user().id)
        except:
            pass
        if new_added_respondets:
            instance.committee_email(new_added_respondets)


m2m_changed.connect(save_committee_users, sender=Committee.users.through)