from django.db import models
from mainapp import ws_methods
from mainapp.positional import PositionalSortMixIn
from meetings.model_files.event import Event
from mainapp.models import CustomModel
from documents.file import File
from django.db import transaction
from django.utils.dateparse import parse_duration, parse_time
from datetime import timedelta
import datetime

# class TopicPositional(PositionalSortMixIn):
#     def save(self, *args, **kwargs):
#         if not self.pk:
#             self.position = len(self.event.topic_set.all())
#         super(TopicPositional, self).save(*args, **kwargs)

class Topic(CustomModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description=models.TextField(blank=True, null=True)
    lead = models.CharField(max_length=200, blank=True)
    duration = models.IntegerField(null=True)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.position = len(self.event.topic_set.all())
        if not self.duration:
            raise Exception('Invalid duration')
        super(Topic, self).save(*args, **kwargs)


    def delete(self):
        topics = Topic.objects.filter(event_id=self.event.id, position__gt=self.position)
        super(Topic, self).delete()
        with transaction.atomic():
            for topic in topics:
                topic.position -=1
                topic.save()


    @classmethod
    def save_agenda_topic(cls, request, params):
        meeting_id = params['meeting_id'];
        name = params['name']
        description = params.get('description')
        lead = params.get('lead')
        duration = params.get('duration')
        # duration = str(duration)
        # duration = cls.set_duration_parse_to_duration(duration)
        topic = Topic(event_id = meeting_id, name=name, description=description,lead=lead,duration=duration)
        topic.save()
        agenda_docs = params.get('agenda_docs')
        agenda_doc_model = ws_methods.get_model('meetings', 'AgendaDocument')
        for agenda_doc in agenda_docs:
            with transaction.atomic():
                doc = File.objects.get(pk=agenda_doc['id'])
                a_doc = agenda_doc_model(agenda_id=topic.id)
                a_doc = ws_methods.duplicate_file(a_doc, doc, file_type='topic')
                a_doc.save()
        # topic_duration = cls.set_duration_to_hour_min(topic.duration)
        data = {
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'lead': topic.lead,
            'duration': topic.duration,
            'position': topic.position,
            'docs':topic.documents.count(),
            'votings': topic.voting_set.count(),
            'surveys': topic.survey_set.count()
        }
        return data
    

    @classmethod
    def delete_agenda_topic(cls, request, params):
        topic_id = params['topic_id']
        topic = Topic.objects.get(pk=topic_id)
        topic.delete()
        topics = Event.get_topics(topic.event)
        return topics

    @classmethod
    def update_positions(cls, request, params):
        topics = params['topics']
        res = []
        with transaction.atomic():
            for topic in topics:
                Topic.objects.filter(pk=topic['id']).update(position=topic['position'])
        return 'done'

    @classmethod
    def update_agenda_topic(cls, request, params):
        topic_id = params['topic_id']
        topic = Topic.objects.get(pk=topic_id)
        for key in params:
            if key != "agenda_docs" and key != "meeting_id" and key != "duration" :
                setattr(topic,key,params[key])
        topic.duration = params.get("duration")
        topic.save()
        agenda_docs = params.get('agenda_docs')
        agenda_doc_model = ws_methods.get_model('meetings', 'AgendaDocument')
        for agenda_doc in agenda_docs:
            with transaction.atomic():
                doc = File.objects.get(pk=agenda_doc['id'])
                a_doc = agenda_doc_model(agenda_id=topic.id)
                a_doc = ws_methods.duplicate_file(a_doc, doc, file_type='topic')
                a_doc.save()
        data = {
            'id': topic.id,
            'name': topic.name,
            'description': topic.description,
            'lead': topic.lead,
            'duration': topic.duration,
            'position': topic.position,
            'docs':topic.documents.count(),
            'votings': topic.voting_set.count(),
            'surveys': topic.survey_set.count()
        }
        return data
    @classmethod
    def set_duration_parse_to_duration(cls,duration):
        duration = duration + ":00"
        duration = parse_duration(duration)
        return duration
    
    @classmethod
    def set_duration_to_hour_min(cls,topic_duration):
        if topic_duration.days <= 10:
            time = str(datetime.timedelta(seconds=topic_duration.seconds)).split(":")
            if int(time[0]) < 10:
                hour = "0" + str(time[0])
            else:
                hour = str(time[0])
            time = hour + ":" + str(time[1])
        else:
            days_to_hours = topic_duration.days * 24
            time = str(datetime.timedelta(seconds=topic_duration.seconds)).split(":")
            hour = time[0]+days_to_hours
            time = str(hour) + ":" + str(time[1])
        return time

    @classmethod
    def check_duration(cls, request, params):
        topics = []
        data = {}
        total_time=''
        if params.get('duration'):
            duration = params['duration']
            duration_after_parse = cls.set_duration_parse_to_duration(duration)
        else:
            duration = False
            duration_after_parse = False
        meeting_id = params['meeting_id'];
        event = Event.objects.get(pk=meeting_id)
        meeting_durration = event.duration
        topics = event.topic_set.all()
        total_hours = 0
        total_minuets = 0
        total_seconds = 0
        if topics:
            for topic in topics:
                topic_duration =  topic.duration
                total_seconds += topic_duration.seconds
            topics_duration =str(datetime.timedelta(seconds=total_seconds)).split(":")
            total_hours = int(topics_duration[0]) 
            total_minuets = int(topics_duration[1])
        if total_hours >= 0 and total_minuets > 60:
            extra_hours = str(timedelta(minutes=total_minuets))[:-3]
            extra_hours = extra_hours.split(":")
            total_hours += int(extra_hours[0])
            total_minuets = int(extra_hours[1])
        total_time = str(total_hours) + ":" + str(total_minuets)
        total_time = cls.set_duration_parse_to_duration(total_time)
        meeting_durration = parse_duration(meeting_durration)
        if (meeting_durration.days >= total_time.days) or (meeting_durration.seconds >= total_time.seconds):
            difference = meeting_durration- total_time
            data['valid_time']  = cls.set_duration_to_hour_min(difference)
            data['meeting_duration'] = cls.set_duration_to_hour_min(meeting_durration)
            data['topics_duration'] = cls.set_duration_to_hour_min(total_time)

            if duration_after_parse and (difference >= duration_after_parse):
                
                if (difference >= duration_after_parse):
                    data['is_valid'] = True
                    message = "Time is valid"
                elif  (difference < duration_after_parse):
                    data['is_valid'] = False
                    message = "Time is not valid. You have only: " + data['valid_time']
            else:
                if not duration:
                    if meeting_durration > total_time:
                        data['is_valid'] = True
                        message = "Time is not valid. You have only: " + data['valid_time']
                    else:
                        data['is_valid'] = False
                        message = "Time is not valid. You have only: " + data['valid_time']
                else:
                    data['is_valid'] = False
                    message = "Time is not valid. You have only: " + data['valid_time']
            
        else:
            data['is_valid'] = False
            message = "Sorry You meeting time is less"
        data['message'] = message
        # data = {'data': valid}
        return data



    def get_attendees(self):
        attendees_list = []
        attendees_list = self.event.get_attendees()
        return attendees_list


    @classmethod
    def get_details(cls, request, params):
        try:
            topic_id = params['id']
            user_id = request.user.id
            topic_orm = Topic.objects.get(pk=topic_id)
            topic = ws_methods.obj_to_dict(topic_orm, fields=['id', 'name', 'lead', 'description', 'duration', 'event__exectime', 'event__name', 'event__id'])
            # topic_duration = cls.set_duration_to_hour_min(topic['duration'])
            topic['duration'] = topic['duration']
            topic_docs = list(topic_orm.documents.values())
            meeting_type = ''
            votings = topic_orm.voting_set.all()
            topic_votings = []
            for voting in votings:
                topic_votings.append({
                    'id': voting.id,
                    'name': voting.name,
                    'open_date': voting.open_date,
                    'close_date': voting.close_date,
                    'voting_type__name': voting.voting_type.name,
                    'is_respondent': voting.is_respondent(user_id),
                    'my_status': voting.get_my_status(voting.id, user_id)
                })
            topic['votings'] = topic_votings
            surveys = topic_orm.survey_set.all()
            topic_surveys = []
            for survey in surveys:
                topic_surveys.append({
                    'id': survey.id,
                    'name': survey.name,
                    'open_date': survey.open_date,
                    'close_date': survey.close_date,
                    'is_published': survey.is_published,
                    'description': survey.description,
                    'is_attempted': survey.is_attempted(survey, user_id),
                    'my_status': survey.my_status(user_id)
                })
            topic['surveys'] = topic_surveys
            try:
                meeting_type = topic_orm.event.exectime
            except:
                pass
            topic['meeting_type'] = meeting_type
            topic['docs'] = topic_docs
            return topic
        except:
            return 'someting went wrong..!'

    @classmethod
    def get_meeting_topics(cls, reques, params):
        meeting_id = params['meeting_id']
        model = params.get('model')
        object_id = params.get('object_id')
        topics = []
        selected_topic_id = 0
        if model and object_id:
            model_obj = ''
            if model == 'voting':
                model_obj = ws_methods.get_model('voting', 'voting')
                voting_obj = model_obj.objects.filter(pk=object_id, meeting_id=meeting_id).values('topic__id')
                if voting_obj:
                    voting_obj = voting_obj[0]
                    selected_topic_id = voting_obj['topic__id']
            if model == 'survey':
                model_obj = ws_methods.get_model('survey', 'survey')
                suvey_obj = model_obj.objects.filter(pk=object_id, meeting_id=meeting_id).values('topic__id')
                if suvey_obj:
                    suvey_obj = suvey_obj[0]
                    selected_topic_id = suvey_obj['topic__id']

        topic_obj = Topic.objects.filter(event_id=meeting_id).values('id', 'name')
        for topic in topic_obj:
            if selected_topic_id:
                if selected_topic_id == topic['id']:
                    topic = {'id': topic['id'], 'name': topic['name'], 'selected': True}
                else:
                    topic = {'id': topic['id'], 'name': topic['name'], 'selected': False}
            else:
                topic = {'id': topic['id'], 'name': topic['name'], 'selected': False}
            topics.append(topic)
        return {'topics': topics, 'selected': selected_topic_id}