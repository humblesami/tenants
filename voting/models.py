import base64
import datetime

import pytz
from django.db import models
from django.db.models import Q
from documents.file import File
from django.db.models import Count
from django.db.models.signals import m2m_changed
from django_currentuser.middleware import get_current_user
from mainapp import ws_methods
from meetings.models import Profile, Event, Topic
from mainapp.ws_methods import send_email_on_creation
from actions.models import Actions
from mainapp.models import CustomModel
from restoken.models import PostUserToken


class VotingType(CustomModel):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name



class VotingChoice(CustomModel):
    name = models.CharField('Voting Choice', max_length = 100)
    voting_type = models.ForeignKey(VotingType, on_delete = models.CASCADE)
    def __str__(self):
        return self.name

from mainapp.settings import server_base_url

class Voting(Actions):
    voting_type = models.ForeignKey(VotingType, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, on_delete=models.SET_NULL, blank=True)
    signature_required = models.BooleanField('Signature Required', blank=True, default=False)
    enable_discussion = models.BooleanField('Enable Discussion', blank=True, default=False)
    public_visibility = models.BooleanField('Results Visible To All', blank=True, default=False)
    my_status = models.CharField(max_length=50, default='pending')

    previous_respondents = []


    @property
    def state(self):
        user_id = get_current_user().id
        user_pendings = 0
        if self.is_respondent(user_id):
            user_pendings = 1 - self.votinganswer_set.filter(user_id=user_id).count()
        total_pendings = len(self.get_audience()) - self.votinganswer_set.all().count()
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
            super(Voting, self).save(*args, **kwargs)
            if create:
                new_added_respondets = self.get_audience()
            
            if new_added_respondets:
                self.send_email_on_save(new_added_respondets)
        except:
            raise


    def send_email_on_save(self, audience, action=None):
        choices_sets = self.voting_type.votingchoice_set.all()
        choices = []
        token_required = False
        for choices_set in choices_sets:
            choices.append({'id':choices_set.id, 'name': choices_set.name})
        template_data = {            
            'id': self.id, 
            'name': self.name,
            'choices': choices,
            'server_base_url': server_base_url                
        }
        post_info = {}
        post_info['res_app'] = self._meta.app_label
        post_info['res_model'] = self._meta.model_name
        post_info['res_id'] = self.id
        if action:
            template_name = 'voting/removed_from_voting_email.html'
            token_required = 'remove'
        else:
            template_name = 'voting/submit_email.html'
            token_required = True
        email_data = {
            'subject': self.name,
            'audience': audience,
            'post_info': post_info,
            'template_data': template_data,
            'template_name': template_name,
            'token_required': token_required
        }
        send_email_on_creation(email_data)


    @classmethod
    def get_pending_votings(cls, user):
        uid = user.id
        votings = Actions.get_my_open_actions(Voting.objects.all(), user, 'home')
        pending_votings = []
        for voting in votings:
            if voting:
                user_answer = VotingAnswer.objects.filter(voting_id=voting.id, user_id=uid)
                if len(user_answer) > 0:
                    user_answer = user_answer[0]
                    my_status = user_answer.user_answer.name
                else:
                    my_status = 'pending'
                    pending_votings.append({
                        'id': voting.id,
                        'name': voting.name,
                        'voting_type_name': voting.voting_type.name,
                        'my_status': my_status,
                        'open_date':str(voting.open_date)
                    })
        return pending_votings

    def mail_audience(self):
        res = []
        tokens = []
        params = {}
        params['res_app'] = 'voting'
        params['res_model'] = 'Voting'
        params['res_id'] = self.id
        if self.meeting:
            for obj in self.meeting.attendees.all():
                res.append(obj.profile.email)
                params['user'] = obj.profile
                token = PostUserToken.create_token(params)
                tokens.append(token)
        else:
            for obj in self.respondents.all():
                res.append(obj.profile.email)
                params['user'] = obj.profile
                token = PostUserToken.create_token(params)
                tokens.append(token)
        return res, tokens

    
    def get_updated_audience(self):
        new_added_respondets = []
        removed_respondents = []
        voting_obj = Voting.objects.get(pk=self.id)
        if voting_obj.meeting and self.meeting:
            new_added_respondets = list(set(self.meeting.get_audience()) - set(voting_obj.meeting.get_audience()))
            removed_respondents = list(set(voting_obj.meeting.get_audience()) - set(self.meeting.get_audience()))
        elif voting_obj.respondents and self.meeting:
            new_added_respondets = list(set(self.meeting.get_audience()) - set(voting_obj.get_audience()))
            removed_respondents = list(set(voting_obj.get_audience()) - set(self.meeting.get_audience()))
        elif voting_obj.respondents and self.respondents:
            new_added_respondets = list(set(self.get_audience()) - set(voting_obj.get_audience()))
            removed_respondents = list(set(voting_obj.get_audience()) - set(self.get_audience()))
        elif voting_obj.meeting and self.respondents:
            new_added_respondets = list(set(self.get_audience()) - set(voting_obj.meeting.get_audience()))
            removed_respondents = list(set(voting_obj.meeting.get_audience()) - set(self.get_audience()))
        return new_added_respondets, removed_respondents
    
    
    def get_my_status(self, voting_id, user_id):
        my_status = ''
        user_answer = VotingAnswer.objects.filter(voting_id = voting_id, user_id=user_id)
        if len(user_answer) > 0:
            user_answer = user_answer[0]
            my_status = user_answer.user_answer.name
        return my_status

    @classmethod
    def get_details(cls, request, params):
        voting_id = params['id']
        voting_object_orm = None
        token = params.get('token')
        if token:
            post_info = {
                'id': voting_id,
                'model': 'Voting',
                'app': 'voting'
            }
            res = PostUserToken.validate_token_for_post(token, post_info)
            if type(res) is str:
                return res
            else:
                request.user = res.user
        
        uid = request.user.id
        if voting_id == 'new':
            if not uid:
                return 'Invalid resolution id'
            voting_object_orm = Voting.objects.filter(created_by_id=uid).last()
            if voting_object_orm:
                voting_id = voting_object_orm.id
        else:
            voting_object_orm = Voting.objects.get(pk=voting_id)
        voting_object = voting_object_orm.__dict__
        voting_object['open_date'] = str(voting_object['open_date'])
        voting_object['close_date'] = str(voting_object['close_date'])

        voting_object['voting_docs'] = []
        try:
            voting_docs = list(voting_object_orm.documents.all().values())
            for doc in voting_docs:
                doc['created_at'] = str(doc['created_at'])
                voting_object['voting_docs'].append(doc)
        except:
            pass
        voting_object['voting_type'] = {
            'id': voting_object_orm.voting_type.id,
            'name': voting_object_orm.voting_type.name
        }
        progress_data = []
        voting_options = []
        try:
            voting_options = list(voting_object_orm.voting_type.votingchoice_set.all())
        except:
            pass

        voting_object['chart_data'] = []
        voting_object['progress_data'] = []
        is_attendee = uid in voting_object_orm.get_audience()
        voting_object['is_attendee'] = is_attendee
        voting_object['voting_options'] = []
        for option in voting_options:
            voting_object['voting_options'].append({'id': option.id, 'name': option.name})
            voting_object['chart_data'].append({'option_name': option.name, 'option_result': 0, 'option_perc': 0})

        voting_results = VotingAnswer.objects.values('user_answer__name').filter(voting_id=voting_id, user_id__in=voting_object_orm.get_audience()).annotate(
            answer_count=Count('user_answer'))
        voting_object['results'] = {
            'answer_count': len(voting_results),
            'respondent_count': len(voting_object_orm.get_audience())
        }
        answer_count = 0
        if voting_results:
            for result in voting_results:
                total = len(voting_results)
                for chart_data in voting_object['chart_data']:
                    if chart_data['option_name'] == result['user_answer__name']:
                        chart_data['option_result'] = result['answer_count']
                        if voting_object['results']['respondent_count']:
                            chart_data['option_perc'] ="{:.{}f}".format((result['answer_count']/voting_object['results']['respondent_count']) *100,2)
                answer_count += result['answer_count']

        my_status = ''
        user_answer = VotingAnswer.objects.filter(voting_id = voting_id, user_id=uid)
        if len(user_answer) > 0:
            user_answer = user_answer[0]
            my_status = user_answer.user_answer.name
            voting_object['signature_data'] = user_answer.signature_data.decode('utf-8')
        else:
            voting_object['my_status'] = 'pending'
        voting_object['meeting'] = []
        voting_object['topic'] = []
        meeting = voting_object_orm.meeting
        if meeting:
            voting_object['meeting'].append({'id': meeting.id, 'name': meeting.name})
        topic = voting_object_orm.topic
        if voting_object['results']['respondent_count']:
            progress_data.append({
                'option_name': 'Response Required',
                'option_result': voting_object['results']['respondent_count'] - answer_count
            })            
            progress_data.append({
                'option_name': 'Responsed',
                'option_result': answer_count
            })
        voting_object['progress_data'] = progress_data

        if topic:
            voting_object['topic'].append({'id': topic.validate_unique()})
        if voting_object.get('_state'):
            del voting_object['_state']
        if my_status:
            voting_object['my_status'] = my_status
        ws_methods.stringify_fields(voting_object)
        return voting_object


    @classmethod
    def get_records(cls, request, params):
        kw = params.get('kw')
        states = params['states']
        user_id = request.user.id
        docs = []
        votings = []
        if kw:
            votings = ws_methods.search_db({'kw': kw, 'search_models': {'voting': ['Voting']}})
        else:
            votings = Voting.objects.all().order_by('-pk')
            
        # votings = Actions.get_my_open_actions(votings, request.user)
        votings = cls.get_actions_against_states(votings, states, request.user)
        offset = params.get('offset')
        limit = params.get('limit')
        total_cnt = len(votings)
        uid = request.user.id
        if limit:
            votings = votings[offset: offset + int(limit)]
        all_votings = []
        count = len(votings)
        for voting in votings:
            current_voting = ws_methods.obj_to_dict(voting, fields=['id', 'name', 'open_date', 'close_date',''])
            current_voting['voting_type'] = voting.voting_type.name
            current_voting['is_respondent'] = uid in voting.get_audience()
            all_votings.append(current_voting)
        votings_json = {'records': all_votings, 'total': total_cnt, 'count': count}
        return votings_json

    
def respondents_saved(sender, instance, action, pk_set, **kwargs):
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


m2m_changed.connect(respondents_saved, sender=Voting.respondents.through)

from restoken.models import PostUserToken

class VotingAnswer(models.Model):
    voting = models.ForeignKey(Voting, on_delete = models.CASCADE, null=True)
    user = models.ForeignKey(Profile, on_delete = models.SET_NULL, blank = False, null=True)
    signature_data = models.BinaryField('Signature Data', default=b'', null=True, blank=True)
    user_answer = models.ForeignKey(VotingChoice, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user_answer.name

    @classmethod
    def answer(cls, request, params):
        voting_id = params.get('voting_id')
        choice_id = params.get('answer')
        user_id = request.user.id
        if not user_id:
            return 'User not found...'

        if choice_id:
            choice_id = int(choice_id)
        else:
            return 'Choice Not Found..'
        signature_data = params.get('signature_data')
        if signature_data:
            signature_data = base64.encodebytes(signature_data.encode())
            cls.update_Choice(choice_id, voting_id, user_id, signature_data)
            return {'data': 'Thanks Your Answer is Updated Successfully..!'}

        option_id = params.get('answer_id', False)
        signature_data = params.get('signature_data', False)
        if signature_data:
            signature_data = base64.encodebytes(signature_data.encode())
        if option_id:
            try:
                cls.update_Choice(option_id, voting_id, user_id, signature_data)
                return {'data':'Answer Updated Successfully.'}
            except:
                cls.save_Choice(option_id, voting_id, user_id, signature_data)
                return {'data':'Answer Saved Successfully.'}

        elif voting_id:
            chart_data = {}
            voting_choices = list(
                VotingChoice.objects.filter(voting_type=Voting.objects.get(pk=voting_id).voting_type.id))
            chart_data['option_data'] = []
            chart_data['option_results'] = []
            for option in voting_choices:
                chart_data['option_data'].append({'id': option.id, 'name': option.name})
                chart_data['option_results'].append({'option_name': option.name, 'option_result': 0})

            voting_results = VotingAnswer.objects.values('user_answer__name').filter(
                voting_id=voting_id).annotate(answer_count=Count('user_answer'))
            # count = voting_results

            if voting_results:
                for result in voting_results:
                    total = len(voting_results)
                    for extra_result in chart_data['option_results']:
                        if extra_result['option_name'] == result['user_answer__name']:
                            extra_result['option_result'] = result['answer_count']

        voting_answer = VotingAnswer.objects.get(voting_id=voting_id, user_id=request.user.id)
        data = {
            'answer': voting_answer.answer.name,
            'signature_data': base64.decodestring(voting_answer.signature_data),
            'chart_data': chart_data['option_results']
        }
        return data

    @classmethod
    def update_my_status(self, choice_id, voting_id):
        voting_choice = VotingChoice.objects.get(pk=choice_id)
        voting = Voting.objects.get(pk=voting_id)
        voting.my_status = voting_choice.name
        voting.save()

    @classmethod
    def save_Choice(cls, choice_id, voting_id, user_id, signature_data):
        signature_required = False
        if signature_data:
            signature_data = signature_data.encode()
        else:
            signature_required = Voting.objects.get(pk=voting_id).signature_required
            if signature_required:
                return 'Please provide signature to submit response'
        voting_answer = VotingAnswer(user_answer_id=choice_id,voting_id = voting_id, user_id = user_id)
        if signature_required:
            voting_answer.signature_data = signature_data
        voting_answer.save()
        cls.update_my_status(choice_id, voting_id)
        return voting_answer

    @classmethod
    def update_Choice(cls, voting_answer, choice_id, signature_data):
        voting_answer.user_answer_id = int(choice_id)
        if signature_data:
            signature_data = signature_data.encode()
            voting_answer.signature_data = signature_data
        voting_answer.save()
        cls.update_my_status(choice_id, voting_answer.voting_id)

    @classmethod
    def submit(cls, request, params):
        voting_id = params.get('voting_id')
        user_answer_id = params.get('voting_option_id')
        token = params.get('token')
        if token:
            post_info = {
                'id': voting_id,
                'model': 'Voting',
                'app': 'voting'
            }
            res = PostUserToken.validate_token(token)
            if type(res) is str:
                return res
            else:
                if not res:
                    return 'Invalid or expired token'
                request.user = res.user
        user_id = request.user.id
        chart_data = []
        res_data = {'error': 'Unknown result'}
        if voting_id:
            voting_object = Voting.objects.get(pk=voting_id)
            if voting_object:
                voting_answer = VotingAnswer.objects.filter(voting_id = voting_id, user_id = user_id)
                if user_answer_id:
                    signature_data = ''
                    if voting_object.signature_required:
                        signature_data = params.get('signature_data')
                        if not signature_data:
                            return 'Please provide signature'
                    if voting_answer:
                        voting_answer = voting_answer[0]
                        cls.update_Choice(voting_answer, user_answer_id, signature_data)
                        res = 'Update'
                    else:
                        voting_answer = cls.save_Choice(user_answer_id, voting_id, user_id, signature_data)
                        res = 'Created'

                voting_options = list(voting_object.voting_type.votingchoice_set.values())
                respondent_count = len(voting_object.get_audience())
                answer_count = 0
                if respondent_count > 0:
                    for option in voting_options:
                        chart_data.append({'option_name': option['name'], 'option_result': 0, 'option_perc': 0})

                    voting_results = VotingAnswer.objects.values('user_answer__name').filter(voting_id=voting_id).annotate(
                        answer_count=Count('user_answer'))
                    if voting_results:
                        for result in voting_results:
                            for data in chart_data:
                                if data['option_name'] == result['user_answer__name']:
                                    data['option_result'] = result['answer_count']
                                    data['option_perc'] = result['answer_count']/respondent_count*100
                            answer_count += result['answer_count']
                progress_data = []
                progress_data.append({
                    'option_name': 'Response Required',
                    'option_result': respondent_count - answer_count
                })            
                progress_data.append({
                    'option_name': 'Responsed',
                    'option_result': answer_count
                })
                res_data = {
                    'voting_option_id': user_answer_id,
                    'chart_data': chart_data,
                    'progress_data': progress_data
                }
            else:
                return 'Voting object not found'
        else:
            return 'Invalid voting id'

        if token:
            return 'done'
        return res_data


    @classmethod
    def submit_public(cls, request, params):
        token = params.get('token')
        user_token = PostUserToken.validate_token(token)
        if not user_token:
            return { 'error': 'Invalid token'}

        params['user_id'] = user_token.user.id
        
        voting_id = params.get('voting_id')
        user_answer_id = params.get('choice_id')
        
        chart_data = []
        res_data = {'error': 'Unknown result'}
        if voting_id:
            voting_object = Voting.objects.get(pk=voting_id)
            if voting_object:
                voting_answer = VotingAnswer.objects.filter(voting_id = voting_id, user_id = params['user_id'])
                if user_answer_id:
                    signature_data = ''
                    if voting_object.signature_required:
                        signature_data = params.get('signature_data')
                        if not signature_data:
                            return 'Please provide signature'
                    if voting_answer:
                        voting_answer = voting_answer[0]
                        cls.update_Choice(voting_answer, user_answer_id, signature_data)
                        res = 'Update'
                    else:
                        voting_answer = cls.save_Choice(user_answer_id, voting_id, params['user_id'], signature_data)
                        res = 'Created'

                voting_options = list(voting_object.voting_type.votingchoice_set.values())
                for option in voting_options:
                    chart_data.append({'option_name': option['name'], 'option_result': 0})

                voting_results = VotingAnswer.objects.values('user_answer__name').filter(voting_id=voting_id).annotate(
                    answer_count=Count('user_answer'))
                if voting_results:
                    for result in voting_results:
                        for data in chart_data:
                            if data['option_name'] == result['user_answer__name']:
                                data['option_result'] = result['answer_count']
                res_data = 'done'
            else:
                return 'Voting object not found'
        else:
            return 'Invalid voting id'

        return res_data



    @classmethod
    def get_signature(cls, request, params):
        voting_id = params.get('voting_id')
        if voting_id:
            voting_answer = VotingAnswer.objects.get(voting_id=voting_id, user_id=request.user.id)
            signature_data = voting_answer.signature_data
            if signature_data:
                base64.decodestring(signature_data)
                signature_data = signature_data.decode('utf-8')
                data = {
                    'signature': signature_data
                }
            else:
                data = {
                    'signature': ''
                }
        else:
            data = {
                'error': 'Invalid voting id'
            }
        return data


class VotingDocument(File):
    voting = models.ForeignKey('Voting', on_delete=models.CASCADE, related_name='documents')

    def save(self, *args, **kwargs):
        if not self.file_type:
            self.file_type = 'voting'
        super(VotingDocument, self).save(*args, **kwargs)

    @classmethod
    def get_attachments(cls, request, params):
        parent_id = params.get('parent_id')
        docs = File.objects.filter(voting_id=parent_id)
        docs = docs.values('id', 'name')
        docs = list(docs)
        return docs

    @property
    def breadcrumb(self):
        voting_obj = self.voting
        event_obj = {}
        topic_data = {}
        data = []
        if voting_obj.topic:
            topic_obj = voting_obj.topic
            topic_data = {'title': topic_obj.name, 'link': '/topic/' + str(topic_obj.id)}
            if topic_obj.event:
                event_obj = topic_obj.event
        if voting_obj.meeting:
            event_obj = voting_obj.meeting
        
        if event_obj:
                if event_obj.exectime != 'ongoing':
                    data.append({'title': event_obj.exectime, 'link': '/meetings/' + event_obj.exectime})
                data.append({'title': event_obj.name, 'link': '/meeting/' + str(event_obj.id)})
        if topic_data:
            data.append(topic_data)
        if not data:
            data.append({'title': 'Resolutions', 'link': '/actions'})

        data.append({'title': voting_obj.name, 'link': '/voting/' + str(voting_obj.id)})

        return data