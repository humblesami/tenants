# -*- coding: utf-8 -*-
import pytz
import datetime
from django.db import models
from ast import literal_eval
from django.urls import reverse
from django.db.models import Count

from django.db.models.signals import m2m_changed
from django.utils.translation import ugettext_lazy as _
from django_currentuser.middleware import get_current_user

from mainapp import ws_methods
from actions.models import Actions
from mainapp.settings import server_base_url


class Survey(Actions):
    topic = models.ForeignKey('meetings.Topic', on_delete=models.CASCADE, null=True, blank=True)
    need_logged_user = models.BooleanField(
        _("Only authenticated users can see it and answer it"), default=True)
    display_by_question = models.BooleanField(_("Display by question"), default=False)
    template = models.CharField(_("Template"), max_length=255, null=True, blank=True)

    class Meta(object):
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    previous_respondents = []


    @property
    def state(self):
        user_id = get_current_user().id
        user_answers = 0
        user_response = self.responses.filter(user_id=user_id)
        if user_response:
            user_answers = user_response[0].answers.count()
        total_questions = self.questions.count()
        user_pendings = 0
        if self.is_respondent(user_id):
            user_pendings = total_questions - user_answers

        total_pendings = len(self.get_audience()) - self.responses.all().count()
        return self._calculate_action_state(total_pendings, user_pendings)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            new_added_respondets = []
            create = False
            if self.pk is not None:
                if self.meeting:
                    new_added_respondets, removed_respondents = self.get_updated_audience()
                elif len(self.respondents.all()) == 0:
                    new_added_respondets, self.previous_respondents = self.get_updated_audience()
            else:
                create = True
            super(Survey, self).save(*args, **kwargs)
            if create:
                new_added_respondets = self.get_audience()

            if new_added_respondets:
                self.send_email_on_save(new_added_respondets)
        except:
            raise

    def is_attempted(self, survey_obj, user_id):
        is_attempted = False
        question_answered = survey_obj.questions.filter(answers__isnull=False, answers__response__user__id=user_id)
        if question_answered:
            is_attempted = True
        return is_attempted


    def get_updated_audience(self):
        new_added_respondets = []
        removed_respondents = []
        survey_obj = Survey.objects.get(pk=self.id)
        if survey_obj.meeting and self.meeting:
            new_added_respondets = list(set(self.meeting.get_audience()) - set(survey_obj.meeting.get_audience()))
            removed_respondents = list(set(survey_obj.meeting.get_audience()) - set(self.meeting.get_audience()))
        elif survey_obj.respondents and self.meeting:
            new_added_respondets = list(set(self.meeting.get_audience()) - set(survey_obj.get_audience()))
            removed_respondents = list(set(survey_obj.get_audience()) - set(self.meeting.get_audience()))
        elif survey_obj.respondents and self.respondents:
            new_added_respondets = list(set(self.get_audience()) - set(survey_obj.get_audience()))
            removed_respondents = list(set(survey_obj.get_audience()) - set(self.get_audience()))
        elif survey_obj.meeting and self.respondents:
            new_added_respondets = list(set(self.get_audience()) - set(survey_obj.meeting.get_audience()))
            removed_respondents = list(set(survey_obj.meeting.get_audience()) - set(self.get_audience()))
        return new_added_respondets, removed_respondents

    # def is_respondent(self, user):
    #     return user.id in self.get_audience()

    def latest_answer_date(self):
        """ Return the latest answer date.

        Return None is there is no response. """
        min_ = None
        for response in self.responses.all():
            if min_ is None or min_ < response.updated:
                min_ = response.updated
        return min_

    def get_absolute_url(self):
        return reverse("survey-detail", kwargs={"id": self.pk})

    @classmethod
    def get_records(cls, request, params):
        surveys = []
        kw = params.get('kw')
        states = params['states']
        uid = request.user.id
        if kw:
            survey_list = ws_methods.search_db({'kw': kw, 'search_models': {'survey': ['Survey']}})
        else:
            survey_list = Survey.objects.all().order_by('-pk').distinct()
        if params.get('meeting_id'):
            meeting_id = params.get('meeting_id')
            survey_list = survey_list.filter(meeting_id=meeting_id)
        survey_list = cls.get_actions_against_states(survey_list, states, request.user)
        total = len(survey_list)
        offset = params.get('offset')
        limit = params.get('limit')
        if limit:
            survey_list = survey_list[offset: offset + int(limit)]

        for survey in survey_list:
            attempted = False
            question_answered = survey.questions.filter(answers__isnull=False, answers__response__user__id=uid)
            if question_answered:
                attempted = True
            meeting = {}
            if survey.meeting:
                meeting = {'id': survey.meeting.id, 'name': survey.meeting.name}
            surveys.append({
                'id': survey.id,
                'name': survey.name,
                'description': survey.description,
                'is_published': survey.is_published,
                'is_attempted': attempted,
                'meeting': meeting,
                'is_respondent': request.user.id in survey.get_audience(),
                'open_date': str(survey.open_date),
                'close_date': str(survey.close_date),
                'question_count': survey.questions.count()
            })
        count = len(survey_list)
        surveys_json = {'records': surveys, 'total': total, 'count': count}
        return surveys_json

    @classmethod
    def get_details(cls, request, params):
        uid = request.user.id
        survey_id = params['survey_id']
        groups = request.user.groups.values('name')
        survey_obj = None
        if survey_id == 'new':
            if not uid:
                return 'Invalid survey id'
            survey_obj = Survey.objects.filter(created_by_id=uid).last()
            if survey_obj:
                survey_id = survey_obj.id
        else:
            survey_obj = Survey.objects.get(pk=survey_id)
        is_respondent = uid in survey_obj.get_audience()
        if not is_respondent:
            for group in groups:
                if group['name'] in ['Admin', 'Staff']:
                    results_visibility = True
        # if not is_respondent:
        #     return 'Unauthorized to access survey details'
        questions = survey_obj.questions.all()
        survey_questions = []
        for question in questions:
            question_dict = question.__dict__
            if question_dict['_state']:
                del question_dict['_state']
            ws_methods.stringify_fields(question_dict)
            if question_dict['choices']:
                question_dict['choices'] = question_dict['choices'].split(',')
            survey_questions.append(question_dict)
        survey = survey_obj.__dict__
        if survey['_state']:
            del survey['_state']
        ws_methods.stringify_fields(survey)
        survey['questions'] = survey_questions
        survey['open_date'] = str(survey['open_date'])
        survey['close_date'] = str(survey['close_date'])
        survey['is_respondent'] = is_respondent
        return survey

    @classmethod
    def get_pending_surveys(cls, user):
        # surveys = Survey.objects.filter(
        #     (Q(meeting__id__isnull=False) & Q(meeting__attendees__id=uid))
        #     |
        #     Q(respondents__id=uid),
        #     Q(close_date__gte=datetime.datetime.now())
        # )
        surveys = Actions.get_my_open_actions(Survey.objects.all(), user, 'home')
        pending_survey = []
        for survey in surveys:
            user_response = survey.questions.filter(answers__isnull=False, answers__response__user__id=user.id)
            if len(user_response) > 0:
                my_status = 'done'
            else:
                my_status = 'pending'
                pending_survey.append({
                    'id': survey.id,
                    'title': survey.name,
                    'my_status': my_status,
                    'open_date': str(survey.open_date),
                    'description': survey.description,
                })
        return pending_survey

    def my_status(self,user_id):
        user_response = self.questions.filter(answers__isnull=False, answers__response__user__id=user_id)
        if len(user_response) > 0:
            status = 'done'
        else:
            status = 'pending'
        return status
    @classmethod
    def total_users(survey,audience,question):
        pass

    @classmethod
    def get_results(cls, request, params):
        survey_id = params['survey_id']
        uid = request.user.id
        groups = request.user.groups.values('name')
        survey = Survey.objects.get(pk=survey_id)
        attempted = False
        question_answered = survey.questions.filter(answers__isnull=False, answers__response__user__id=uid)
        if question_answered:
            attempted = True
        audience = survey.get_audience()
        is_respondent = uid in audience
        if not is_respondent:
            for group in groups:
                if group['name'] in ['Admin', 'Staff']:
                    is_respondent = True
        if not is_respondent:
            return 'Not authorized to see results'
        is_open = False
        utc=pytz.UTC
        now = datetime.datetime.now().replace(tzinfo=utc)
        survey.close_date = survey.close_date.replace(tzinfo=utc)
        if survey.close_date > now:
            is_open = True
        survey_results = {
            'id': survey.id,
            'name': survey.name,
            'questions': [],
            'questions_single':[],
            'questions_multi':[],
            'is_open': is_open,
            'is_published': survey.is_published,
            'publish': survey.is_published,
            'is_respondent': request.user.id in survey.get_audience(),
            'is_attempted': attempted,
            'progess_data': []
        }
        questions = survey.questions.all()
        for question in questions:
            question_choices = []
            user_answers = []
            if question.type in ('radio', 'select-multiple'):
                question_choices = question.choices.split(',')
            answers = list(question.answers.values('id','body', 'response__user__username').annotate(answer_count=Count('body')))
            # answer_objects = question.answers.all()
            # answer_objects = question.answers.filter(response__user__id=1)
            cnt = 0
            user_answers_count = 0
            for answer in answers:
                user_answer = answer['body']
                if question.type == 'select-multiple':
                    user_answer = literal_eval(user_answer)
                    user_answers_count += len(user_answer)
                profile_model = ws_methods.get_model('meetings', 'Profile')
                # user_response = answer_objects[cnt].response
                answer_objects = question.answers.get(pk=answer['id'])
                user_response = answer_objects.response
                # user_response = answer_objects.filter(updated_by_id=)
                if user_response and user_response.user:
                    answer_user = profile_model.objects.filter(pk=user_response.user.id)
                    cnt += 1
                    if answer_user:
                        answer_user = answer_user[0]
                        user_answers.append({
                            'answers': user_answer,
                            'user_name': answer['response__user__username'],
                            'user': {
                                'id': answer_user.id,
                                'name': answer_user.fullname(),
                                'email': answer_user.email,
                                'photo': answer_user.image.url,
                            }
                        })
            question_data = []
            chart_data = []
            for choice in question_choices:
                question_data.append({'option_name': choice.strip(), 'option_result': 0, 'option_perc': 0, 'total_perc': 0, 'type':'','total_answers':''})
            for index, user_answer in enumerate(answers):
                if question.type == 'select-multiple':
                    user_answer = literal_eval(user_answer['body'])

                    for user_ans in user_answer:
                        for singledata in question_data:
                            if user_ans == singledata['option_name'].replace(' ','-').lower():
                                singledata['option_result'] += 1
                                singledata['option_perc'] = "{:.{}f}".format( singledata['option_result'] / len(audience) * 100, 2 )
                                singledata['total_perc'] = "{:.{}f}".format((singledata['option_result']/ user_answers_count ) * 100,2)
                                singledata['total_answers'] = user_answers_count
                                singledata['type'] = 'select-multiple'
                                break
                else:
                    for singledata in question_data:
                        if user_answer['body'] == singledata['option_name'].replace(' ', '-').lower():
                            singledata['option_result'] = user_answer['answer_count'] + singledata[
                                'option_result']
                            singledata['option_perc'] = "{:.{}f}".format( singledata['option_result'] / len(audience) * 100, 2 )
                
            progress_data = []
            respondents = 0
            if survey.meeting:
                respondents = len(survey.meeting.attendees.all())

            if len(survey.respondents.all()):
                respondents = len(survey.respondents.all())

            if survey.responses:
                responses = len(survey.responses.all())

            progress_data.append({
                'option_name': '',
                'option_result': respondents - responses
            })
            progress_data.append({
                'option_name': '',
                'option_result': responses
            })
            if question.type in ('radio', 'select-multiple'):
                survey_results['questions_multi'].append({
                    'id': question.id,
                    'name': question.text,
                    'choices': question_choices,
                    'user_answers': user_answers,
                    'chart_data': question_data
                })
            else:
                survey_results['questions_single'].append({
                    'id': question.id,
                    'name': question.text,
                    'choices': question_choices,
                    'user_answers': user_answers,
                    'chart_data': question_data
                })
            survey_results['questions'] = survey_results['questions_single'] + survey_results['questions_multi']
            survey_results['progress_data'] = progress_data
        return survey_results


    def send_email_on_save(self, audience, action=None):
        token_required = False
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
            template_name = 'survey/removed_from_survey_email.html'
            token_required = 'remove'
        else:
            template_name = 'survey/survey_creation_email.html'
            token_required = True
        email_data = {
            'subject': self.name,
            'audience': audience,
            'post_info': post_info,
            'template_data': template_data,
            'template_name': template_name,
            'token_required': token_required
        }
        ws_methods.send_email_on_creation(email_data)



def respondent_saved(sender, instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        removed_respondents = list(pk_set)
        instance.send_email_on_save(removed_respondents, 'removed')
    if action == "post_add":
        new_added_respondets = list(pk_set)
        if instance.previous_respondents:
            removed_respondents = list(set(instance.previous_respondents) - set(new_added_respondets))
            new_added_respondets = list(set(new_added_respondets) - set(instance.previous_respondents))
            if new_added_respondets:
                instance.send_email_on_save(new_added_respondets)
            if removed_respondents:
                instance.send_email_on_save(removed_respondents, 'removed')
        else:
            instance.send_email_on_save(new_added_respondets)
m2m_changed.connect(respondent_saved, sender=Survey.respondents.through)