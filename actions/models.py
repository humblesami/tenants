import pytz
import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mainapp.models import CustomModel
from meetings.model_files.event import Event


class Actions(CustomModel):
    class Meta:
        abstract = True
    open_date = models.DateTimeField(default=None)
    close_date = models.DateTimeField(default=None)
    meeting = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, blank=True)
    name = models.CharField(_("Name"), max_length=400)
    description = models.TextField(_("Description"), default='')
    respondents = models.ManyToManyField('meetings.Profile', blank=True)
    is_published = models.BooleanField(_("Publish"), default=False)


    def _calculate_action_state(self, total_pendings, user_pendings):
        utc=pytz.UTC
        today = utc.localize(datetime.datetime.now())
        close_date = self.close_date
        if not self.is_published:
            return 'draft'
        elif total_pendings == 0:
            return 'completed'
        elif today > close_date:
            return 'incomplete'
        elif user_pendings > 0:
            return 'to do'
        else:
            return 'in progress'
        # else:
        #     return 'in progress'

    def save(self, *args, **kwargs):
        super(Actions, self).save(*args, **kwargs)

    def __str__(self):
        return self.meeting.name + '-Action'

    def is_respondent(self, user_id):
        is_respondent = False
        respondents = self.get_respondents()
        if user_id in respondents:
            is_respondent = True
        return is_respondent

    def get_respondents(self):
        res = []
        # if self.meeting:
        #     return self.meeting.get_audience()
        # else:
        #     res = []
        for obj in self.respondents.all():
            res.append(obj.id)
        return res
    
    def get_audience(self):
        audience = []
        for obj in self.respondents.all().values('id'):
            audience.append(obj['id'])
        return list(dict.fromkeys(audience))

    @classmethod
    def get_my_open_actions(self, query_result, user, home_page=None):
        exclude_ids = []
        if not home_page:
            groups = user.groups.all().values('name')
            for group in groups:
                if group['name'] in ['Admin', 'Staff']:
                    return query_result
        uid = user.id
        for action in query_result:
            audience = action.get_audience()
            is_respondent = uid in audience
            if not is_respondent:
                exclude_ids.append(action.id)
                continue
            is_open = True
            utc = pytz.UTC
            now = datetime.datetime.now().replace(tzinfo=utc)
            action.close_date = action.close_date.replace(tzinfo=utc)
            if action.open_date > now:
                is_open = False
            elif action.close_date <= now:
                is_open = False
            if not is_open:
                exclude_ids.append(action.id)
        query_result = query_result.exclude(id__in=exclude_ids)
        return query_result
    

    @classmethod
    def change_status(self, action, params):
        status = params['status']
        action_id = params['id']
        action = action.objects.get(pk=action_id)
        if not action:
            return 'Action not Found'
        action.status = status
        action.save()
        params['status'] = not status
        return params
    
    def get_actions_against_states(actions, state, user):
        to_be_return_actions = []
        actions = Actions.get_my_open_actions(actions, user)
        states = ['to do']
        if state:
            states = [state]
            if state == 'completed' or state == 'incomplete':
                states = ['completed', 'incomplete']
        for action in actions:
            if action.state in states:
                to_be_return_actions.append(action)
        return to_be_return_actions