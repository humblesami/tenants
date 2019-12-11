import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_countries.fields import CountryField
from django.db.models.signals import m2m_changed
from django.utils.translation import gettext_lazy as _

from mainapp import ws_methods
from mainapp.models import CustomModel
from mainapp.settings import server_base_url
from restoken.models import PostUserToken
from meetings.model_files.user import Profile


# Create your models here.
class Event(CustomModel):
    class Meta:
        verbose_name = "Meeting"
        verbose_name_plural = "Meetings"
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    attendees = models.ManyToManyField(Profile, related_name="meetings")
    custom_message = models.CharField('Message', max_length=200, blank=True)
    street = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    publish = models.BooleanField(default=False)
    country = CountryField(blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    archived = models.BooleanField(default=False)
    zip = models.CharField(max_length=10, blank=True)
    pin = models.CharField('Meeting PIN', max_length=50, blank=True, null=True)
    conference_bridge_number = models.CharField('Conference Bridge No.', max_length=200, null=True, blank=True)
    video_call_link = models.CharField(max_length=200, null=True, blank=True)

    def has_active_action(self):
        today = datetime.datetime.now()
        votings = self.voting_set.filter(open_date__lte=today, close_date__gte=today)
        if votings:
            return True
        surveys = self.survey_set.filter(open_date__lte=today, close_date__gte=today)
        if surveys:
            return True
        sign_docs = self.signaturedoc_set.filter(open_date__lte=today, close_date__gte=today)
        if sign_docs:
            return True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        creating = False
        old_attendee_ids = []
        if self.pk:
            old_event = Event.objects.get(pk=self.pk)
            if self.archived != old_event.archived:
                if self.has_active_action():
                    message = 'This meeting can not be archived because some actions are associated with it. let them complete.'
                    raise Exception(message)
            for obj in old_event.attendees.all():
                old_attendee_ids.append(obj.id)
        super(Event, self).save(*args, **kwargs)
        attendee_ids = []
        for obj in self.attendees.all():
            attendee_ids.append(obj.id)

        gone_attendees = set(old_attendee_ids) - set(attendee_ids)
        gone_attendees = list(gone_attendees)
        if len(gone_attendees) > 0:
            to_del = InvitationResponse.objects.filter(event_id=self.id, attendee_id__in=gone_attendees)
            to_del.delete()
        for id in attendee_ids:
            create_obj = InvitationResponse.objects.filter(attendee_id=id, event_id=self.id)
            if not create_obj:
                create_obj = InvitationResponse(attendee_id=id, event_id=self.id)
                create_obj.save()

    def save1(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)

    def notification_text(self):
        name = self.name
        if len(name) > 60:
            name = name[:20] + '...'
        return ' Meeting "' + name

    def get_audience(self):
        res = []
        audience = self.attendees.all().values('id')
        for user in audience:
            res.append(user['id'])
        return res

    @classmethod
    def get_attendees_list(cls, request, params):
        meeting_id = params.get('meeting_id')
        meeting = Event.objects.get(id=meeting_id)
        return Event.attendees_to_list(meeting.attendees.all())

    @classmethod
    def attendees_to_list(cls, attendees):
        attendees_list = []
        for attendee in attendees:
            attendee_groups = attendee.groups.all()
            if attendee_groups:
                group_name = attendee_groups[0].name.lower()
                attendees_list.append({'id': attendee.id, 'name': attendee.name, 'group': group_name})
        return attendees_list

    def get_attendees(self):
        return Event.attendees_to_list(self.attendees.all())

    @property
    def attendance_marked(self):
        unmarked = InvitationResponse.objects.filter(event_id=self.id, attendance__isnull=True).distinct()
        if unmarked:
            return False
        else:
            return True

    @property
    def exectime(self):
        current_date = timezone.now()
        if not self.publish:
            return 'draft'
        if self.start_date >= current_date:
            return 'upcoming'
        elif self.end_date <= current_date and self.archived == False:
            return 'completed'
        elif self.end_date <= current_date and self.archived == True:
            return 'archived'
        elif self.start_date <= current_date and self.end_date >= current_date:
            return 'ongoing'

    def _compute_duration(self):
        val = self.end_date - self.start_date
        seconds = val.total_seconds()
        hours = seconds / 3600
        hours = int(hours)

        rem_seconds = seconds % 3600
        minutes = rem_seconds / 60
        minutes = int(minutes)

        if hours < 10:
            hours = '0' + str(hours)
        else:
            hours = str(hours)
        if minutes < 10:
            minutes = '0' + str(minutes)
        else:
            minutes = str(minutes)
        val = hours + ':' + minutes + ':00'
        return val
    duration = property(_compute_duration)

    def _compute_address(self):
        val = ''
        if self.street:
            val = val + self.street + ', '
        if self.city:
            val = val + self.city + ', '
        if self.state:
            val = val + self.state + ', '
        if self.zip:
            val = val + self.zip + ', '
        if self.country:
            val = val + str(self.country.name)
        if val:
            last_character = val[len(val) - 1]
            if last_character == ' ':
                val = val.strip()
            if last_character == ',':
                val = val[:-1]
        val = val.strip()
        return val

    location = property(_compute_address)

    @classmethod
    def get_calendar(cls, request, params):
        user_id = request.user.id
        public_events = Event.objects.filter(archived=False, publish=True).values('id', 'name', 'start_date', 'end_date')
        calendar_events = []
        for ev1 in public_events:
            ev2 = Event.objects.get(pk=ev1['id'])
            am_participant = ev2.attendees.filter(pk=user_id)
            if am_participant:
                am_participant = 1
            else:
                am_participant = None
            event = {
                'id': ev1['id'],
                'name': ev1['id'],
                'start_date': str(ev1['start_date']),
                'end_date': str(ev1['end_date']),
                'my_event': am_participant,
            }
            calendar_events.append(event)
        return calendar_events

    @classmethod
    def get_upcoming_public_events(cls, user_id):
        public_events = Event.objects.filter(archived=False, publish=True, end_date__gt=datetime.datetime.now())
        calendar_events = []
        for event in public_events:
            event.start_date = str(event.start_date)
            event.end_date = str(event.end_date)
            event.country = str(event.country.name)
            event.start = event.start_date
            event.stop = event.end_date
            my_event = event.attendees.filter(pk=user_id)
            if my_event:
                event.my_event = 1
            event = event.__dict__
            if event['_state']:
                del event['_state']
            ws_methods.stringify_fields(event)
            calendar_events.append(event)
        return calendar_events

    @classmethod
    def get_pending_meetings(cls, uid):
        meetings = Event.objects.filter(attendees__id=uid, publish=True, end_date__gte=datetime.datetime.now())

        pending_meetings = cls.get_meeting_summaries(meetings, uid)
        return pending_meetings

    # working on meeting attendees attendance
    @classmethod
    def mark_attendance(cls, request, params):
        meeting_id = params['meeting_id']
        attendances = params['attendance_data']
        for atten in attendances:
            check_meeting = InvitationResponse.objects.get(event_id=meeting_id, attendee_id=atten['id'])
            check_meeting.attendance = atten['attendance']
            check_meeting.save()
        attendance_marked = Event.objects.get(pk=meeting_id).attendance_marked
        return {'attendance_marked': attendance_marked}

    @classmethod
    def respond_invitation(cls, request, params):
        meeting_id = params['meeting_id']
        user_response = params.get('response')
        user_attendance = params.get('attendance')
        response_by = params.get('response_by')
        token = params.get('token')

        user_id = 0
        if token:
            post_info = {
                'id': meeting_id,
                'model': 'Event',
                'app': 'meetings'
            }
            res = PostUserToken.validate_token(token)
            if type(res) is str:
                return res
            else:
                request.user = res.user
        if request.user.id:
            user_id = request.user.id
        else:
            user_id = params['user_id']
        meeting = Event.objects.get(id=meeting_id)
        is_respondant = meeting.attendees.filter(id=user_id)
        if not is_respondant:
            return 'Unauthorized'
        if user_response:
            ResponseList = InvitationResponse.objects.filter(event_id=meeting_id, attendee_id=user_id)
            if ResponseList:
                ResponseList = ResponseList[0]
                ResponseList.state = user_response
                ResponseList.save()
            else:
                ResponseList = ResponseList(state=user_response, event_id=meeting_id, attendee_id=user_id)
                ResponseList.save()
            return 'done'
        elif user_attendance:
            data = {
                'attendance_marked': False
            }
            user_id = params['user_id']
            ResponseList = InvitationResponse.objects.filter(event_id=meeting_id, attendee_id=user_id)
            if ResponseList:
                ResponseList = ResponseList[0]
                ResponseList.attendance = user_attendance
                ResponseList.save()
                data['attendance_marked'] = ResponseList.event.attendance_marked
            else:
                ResponseList = ResponseList(attendance= user_attendance, event_id = meeting_id, attendee_id = user_id)
                ResponseList.save()
                data['attendance_marked'] = ResponseList.event.attendance_marked
            return data
        return 'Something Wrong in Response Invitation'

    @classmethod
    def get_details(cls, request, params):
        meeting_id = params['id']
        token = params.get('token')
        if token:
            post_info = {
                'id': meeting_id,
                'model': 'Event',
                'app': 'meetings'
            }
            res = PostUserToken.validate_token_for_post(token, post_info)
            if type(res) is str:
                return res
            else:
                request.user = res.user
        user_id = request.user.id
        meeting_object_orm = None
        if meeting_id == 'new':
            if not user_id:
                return 'Invalid meeting id'
            meeting_object_orm = Event.objects.filter(created_by_id=user_id).last()
            if meeting_object_orm:
                meeting_id = meeting_object_orm.id
        else:
            meeting_object_orm = Event.objects.prefetch_related('survey_set', 'voting_set', 'topic_set', 'documents', 'signaturedoc_set').get(pk=meeting_id)

        topic_model = ws_methods.get_model('meetings', 'Topic')
        meeting_object = {}
        location = meeting_object_orm.location
        duration = meeting_object_orm.duration
        meeting_object['id'] = meeting_object_orm.id
        meeting_object['name'] = meeting_object_orm.name
        meeting_object['description'] = meeting_object_orm.description
        meeting_object['location'] = location
        meeting_object['duration'] = duration
        # meeting_object['duration_data'] = topic_model.check_duration( request ,params={"meeting_id":meeting_object_orm.id})

        meeting_object['street'] = meeting_object_orm.street
        meeting_object['city'] = meeting_object_orm.city
        meeting_object['state'] = meeting_object_orm.state
        meeting_object['zip'] = meeting_object_orm.zip
        meeting_object['country'] = meeting_object_orm.country.name

        meeting_object['start_date'] = str(meeting_object_orm.start_date)
        meeting_object['end_date'] = str(meeting_object_orm.end_date)
        meeting_object['start'] = str(meeting_object_orm.start_date)
        meeting_object['stop'] = str(meeting_object_orm.end_date)
        meeting_object['created_by'] = str(meeting_object_orm.created_by)
        meeting_object['updated_by'] = str(meeting_object_orm.updated_by)
        meeting_object['exectime'] = meeting_object_orm.exectime
        meeting_object['publish'] = meeting_object_orm.publish
        meeting_object['attendance_marked'] = meeting_object_orm.attendance_marked
        meeting_object['pin'] = meeting_object_orm.pin
        meeting_object['conference_bridge_number'] = meeting_object_orm.conference_bridge_number
        meeting_object['video_call_link'] = meeting_object_orm.video_call_link
        # meeting_object['pin'] = meeting_object_orm.pin
        # meeting_object['pin'] = meeting_object_orm.pin

        attendance_status = cls.get_attendance_status(meeting_object_orm, user_id)
        meeting_object['attendee_status'] = attendance_status['state']
        meeting_object['my_event'] = attendance_status['my_event']

        topics = cls.get_topics(meeting_object_orm)
        errors = []
        meeting_docs = list(meeting_object_orm.documents.values())

        """attendee needs fix"""
        attendees = []
        meeting_attendees = ws_methods.get_user_info(meeting_object_orm.attendees.filter(groups__name__in=['Admin','Staff','Director']).distinct())
        for attendee_obj in meeting_attendees:
            attendance_status = cls.get_attendance_status(meeting_object_orm, attendee_obj['id'])
            attendee_obj['attendance_status'] = attendance_status['state']
            attendee_obj['response_by'] = attendance_status['response_by']
            attendee_obj['attendance'] = attendance_status['attendance']
            attendee_obj['my_event'] = attendance_status['my_event']
            attendees.append(attendee_obj)
        meeting_object['topics'] = topics

        if token:
            data = {"meeting": meeting_object, "next": 0, "prev": 0}
            return {'data': data, 'errors': errors}

        meeting_object['meeting_docs'] = []
        for doc in meeting_docs:
            doc['created_at'] = str(doc['created_at'])
            meeting_object['meeting_docs'].append(doc)
        esign_docs = []
        sign_docs = meeting_object_orm.signaturedoc_set.all()
        for sign_doc in sign_docs:
            doc = sign_doc.get_pending_sign_count(request.user.id)
            doc['id'] = sign_doc.id
            doc['pdf_doc'] = sign_doc.pdf_doc.url
            doc['name'] = sign_doc.name
            esign_docs.append(doc)
        meeting_object['sign_docs'] = esign_docs
        votings = list(meeting_object_orm.voting_set.all().values('id', 'name', 'open_date', 'close_date', 'description','voting_type__name'))
        for voting in votings:
            voting['open_date'] = str(voting['open_date'])
            voting['close_date'] = str(voting['close_date'])

        surveys_qs = meeting_object_orm.survey_set.all()
        surveys = list(surveys_qs.values('id', 'name', 'description', 'open_date', 'close_date'))
        i = 0
        for obj in surveys_qs:
            surveys[i]['my_status'] = obj.my_status(user_id)
            i = i + 1
        meeting_object['surveys'] = surveys
        meeting_object['votings'] = votings
        meeting_object['attendees'] = attendees
        meeting_object['has_active_action'] = meeting_object_orm.has_active_action()
        data = {"meeting": meeting_object, "next": 0, "prev": 0}
        return {'data': data, 'errors': errors}

    @classmethod
    def get_topics(cls, meeting_object_orm):
        topic_orm = list(meeting_object_orm.topic_set.all().order_by('position'))
        topics = []
        try:
            for t in topic_orm:
                topic = ws_methods.obj_to_dict(t)
                del topic['updated_at']
                del topic['created_at']
                del topic['updated_by']
                del topic['created_by']
                del topic['description']
                topic_duration = 0
                try:
                    topic_duration = topic['duration']
                except:
                    print('Invalid duration of topic ' + t.name + '-' + str(t.id))
                topic['votings'] = t.voting_set.count()
                topic['surveys'] = t.survey_set.count()
                topic['docs'] = t.documents.count()
                topics.append(topic)
        except:
            err = ws_methods.get_error_message()
            print(err)
        return topics

    @classmethod
    def get_attendance_status(cls, meeting, uid):
        ResponseList = InvitationResponse.objects.filter(event_id=meeting.id, attendee_id=uid)
        attendance_status = {
            'state': 'needsAction',
            'response_by': '',
            'attendance': ''
        }
        if ResponseList:
            ResponseList = list(ResponseList)[0]
            attendance_status['state'] = ResponseList.state
            attendance_status['response_by'] = ResponseList.state_by
            attendance_status['attendance'] = ResponseList.attendance
        my_event = meeting.attendees.filter(pk=uid)
        if my_event:
            attendance_status['my_event'] = 1
        else:
            attendance_status['my_event'] = None
        return attendance_status

    @classmethod
    def meeting_summary(cls, request, params):

        meeting = {}
        uid = request.user.id
        meeting_id = int(params['id'])
        meeting_obj = Event.objects.get(pk=meeting_id)
        meeting['id'] = meeting_obj.id
        meeting['name'] = meeting_obj.name
        meeting['start_date'] = str(meeting_obj.start_date)
        meeting['end_date'] = str(meeting_obj.end_date)
        meeting['start'] = str(meeting_obj.start_date)
        meeting['stop'] = str(meeting_obj.end_date)
        meeting['location'] = meeting_obj.location
        attendance_status = cls.get_attendance_status(meeting_obj, uid)
        meeting['attendee_status'] = attendance_status['state']
        meeting['my_event'] = attendance_status['my_event']
        return meeting

    @classmethod
    def get_meeting_summaries(cls, meetings, uid):
        res_meetings = []
        for meeting_obj in meetings:
            meeting = {}
            meeting_id = meeting_obj.id
            meeting['id'] = meeting_obj.id
            meeting['name'] = meeting_obj.name
            meeting['start_date'] = str(meeting_obj.start_date)
            meeting['end_date'] = str(meeting_obj.end_date)
            meeting['start'] = str(meeting_obj.start_date)
            meeting['stop'] = str(meeting_obj.end_date)
            meeting['location'] = meeting_obj.location

            attendance_status = cls.get_attendance_status(meeting_obj, uid)
            meeting['attendee_status'] = attendance_status['state']
            meeting['my_event'] = attendance_status['my_event']
            res_meetings.append(meeting)
        return res_meetings

    @classmethod
    def get_records(cls, request, params):
        offset = params.get('offset')
        limit = params.get('limit')
        meeting_type = params.get('meeting_type')
        meeting_list = cls.get_meetings(meeting_type, params)
        meetings = cls.get_meeting_summaries(meeting_list, request.user.id)
        total = len(meetings)
        if limit:
            meetings = meetings[offset: offset + int(limit)]
        count = len(meetings)
        meetings = {'records': meetings, 'total': total, 'count': count}
        data = {'error': '', 'data': meetings}
        return data

    @classmethod
    def get_meetings(cls, meeting_type, params=None):
        results = None
        kw = params.get('kw')
        if kw:
            results = ws_methods.search_db({'kw': kw, 'search_models': {'meetings': ['Event']}})
        else:
            results = Event.objects.all().order_by('-pk')
        if meeting_type == 'archived':
            meetings = results.filter(archived=True, publish=True)
        elif meeting_type == 'draft':
            meetings = results.filter(publish=False)
        else:
            meetings = results.filter(publish=True)

        meeting_list = []
        for meeting in meetings:
            if meeting_type == 'upcoming':
                if meeting.exectime in (meeting_type, 'ongoing'):
                    meeting_list.append(meeting)
            elif meeting_type == 'draft':
                meeting_list.append(meeting)
            elif meeting.exectime == meeting_type:
                meeting_list.append(meeting)
        return meeting_list

    @classmethod
    def move_to_archive(cls, request, params):
        meeting_id = params['meeting_id']
        meeting_obj = Event.objects.filter(pk=meeting_id, publish=True)
        if meeting_obj:
            meeting_obj = meeting_obj[0]
            if not meeting_obj.attendance_marked:
                return 'Please mark attendance before moving this meeting to Archive'
            if meeting_obj.has_active_action():
                message = 'This meeting can not be archived because some actions are associated with it. let them complete then move this meeting to archive'
                return message
            meeting_obj.archived = True
            meeting_obj.save()
            return 'done'
        return 'Something went wrong while moving meeting to archived'

    @classmethod
    def update_publish_status(cls, request, params):
        meeting_id = params['meeting_id']
        publish_status = params['publish_status']
        meeting_obj = Event.objects.get(pk=meeting_id)
        meeting_obj.publish = publish_status
        meeting_obj.save()
        if meeting_obj.publish:
            meeting_obj.response_invitation_email(meeting_obj.get_audience())
        return {'publish': publish_status}

    @classmethod
    def get_roster_details(cls, request, params):
        meeting_id = params['meeting_id']
        offset = params.get('offset')
        limit = params.get('limit')
        attendees_list = []
        kw = params.get('kw')
        if kw:
            profiles = ws_methods.search_db({'kw': kw, 'search_models': {'meetings': ['Profile']}})
            records = InvitationResponse.objects.filter(event_id=meeting_id, attendee_id__in=profiles.values('id'))
        else:
            records = InvitationResponse.objects.filter(event_id=meeting_id)
        total = len(records)
        # if limit:
        #     records = records[offset: offset + int(limit)]
        for obj in records:
            attendee_data = ws_methods.obj_to_dict(
                obj.attendee,
                fields=['id', 'name', 'email', 'mobile_phone', 'company', 'image']
            )
            attendee_data['status'] = obj.get_state_display() or 'No Response'
            attendee_data['attendance'] = obj.attendance
            attendee_data['photo'] = attendee_data['image']
            attendees_list.append(attendee_data)
        data = {
            'attendees': attendees_list,
            'total': total
        }
        return data

    @classmethod
    def search_roster(cls, request, params):
        key_word = params['key_word']
        meeting_id = params['meeting_id']
        offset = params['offset']
        limit = params['limit']
        data = {
            'attendees': [],
            'total': 0
        }
        meeting_obj = Event.objects.get(pk=meeting_id)
        attendees = meeting_obj.attendees
        attendees = attendees.filter(
            Q(name__contains=key_word) |
            Q(email__contains=key_word) |
            Q(mobile_phone__contains=key_word) |
            Q(company__contains=key_word) |
            Q(InvitationResponse__attendance__contains=key_word)
        ).distinct()
        if attendees:
            total = len(attendees)
            attendees = attendees[offset: offset + limit]
            attendees_list = []
            for attendee in attendees:
                attendee_data = ws_methods.obj_to_dict(
                    attendee,
                    fields=['id', 'name', 'mobile_phone', 'email', 'company', 'image'],
                    related={
                        'InvitationResponse_set': {'fields': 'attendance'}
                    }
                )
                attendee_data['attendance'] = attendee_data['InvitationResponse_set'][0]['attendance']
                del attendee_data['InvitationResponse_set']
                attendee_data['photo'] = attendee_data['image']
                attendees_list.append(attendee_data)
            data['attendees'] = attendees_list
            data['total'] = total
            return data
        return data

    @classmethod
    def get_action_dates(cls, request, params):
        meeting_id = params['meeting_id']
        meeting = Event.objects.get(pk=meeting_id)
        if meeting:
            start_date = meeting.start_date.date()
            start_time = meeting.start_date.time()
            end_date = meeting.end_date.date()
            end_time = meeting.end_date.time()
            data = {
                'open_date': '%04d' % start_date.year + '-' + '%02d' % start_date.month + '-' + '%02d' % start_date.day,
                'open_time': '%02d' % start_time.hour + ':' + '%02d' % start_time.minute + ':' + '%02d' % start_time.second,
                'close_date': '%04d' % end_date.year + '-' + '%02d' % end_date.month + '-' + '%02d' % end_date.day,
                'close_time': '%02d' % end_time.hour + ':' + '%02d' % end_time.minute + ':' + '%02d' % end_time.second
            }
            return data
        else:
            return 'done'

    def response_invitation_email(self, audience, action=None):
        state_selection = []
        for state in STATE_SELECTION:
            if state[0] != 'needsAction':
                if state[0] != 'tentative':
                    state_selection.append({'name': state[1], 'value': state[0]})
                else:
                    state_selection.append({'name': 'Tentative', 'value': state[0]})
        template_data = {
            'id': self.id,
            'name': self.name,
            'response_invitations': state_selection,
            'server_base_url': server_base_url
        }
        post_info = {}
        post_info['res_app'] = self._meta.app_label
        post_info['res_model'] = self._meta.model_name
        post_info['res_id'] = self.id
        if action:
            template_name = 'event/removed_from_meeting_email.html'
            token_required = 'remove'
        else:
            template_name = 'event/response_invitation_email.html'
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


def attendees_saved(sender, instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        if instance.exectime in ['ongoing', 'upcoming'] and instance.publish and not instance.archived:
            removed_respondents = list(pk_set)
            instance.response_invitation_email(removed_respondents, 'removed')
            InvitationResponse.objects.filter(attendee_id__in=removed_respondents).delete()
    if action == "post_add":
        if instance.exectime in ['ongoing', 'upcoming'] and instance.publish and not instance.archived:
            new_added_respondets = list(pk_set)
            if new_added_respondets:
                instance.response_invitation_email(new_added_respondets)
                respond_objs = []
                for user_id in new_added_respondets:
                    respond_obj = InvitationResponse(event_id=instance.id, attendee_id=user_id)
                    respond_objs.append(respond_obj)
                if respond_objs:
                    InvitationResponse.objects.bulk_create(respond_objs)


m2m_changed.connect(attendees_saved, sender=Event.attendees.through)

STATE_SELECTION = (
    ('needsAction', _("Needs Action")),
    ('tentative', _("Uncertain")),
    ('declined', _("Declined")),
    ('accepted', _("Accepted")),
)
ATTENDANCE_SELECTION = (
    ('absent', _("Absent")),
    ('inperson', _("Inperson")),
    ('online', _("Online")),
)


class InvitationResponse(CustomModel):
    state = models.CharField(max_length=20, choices=STATE_SELECTION, blank=True, null=True)
    state_by = models.CharField(max_length=20, blank=True, null=True)
    attendee = models.ForeignKey(Profile, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendance = models.CharField(max_length=20, choices=ATTENDANCE_SELECTION, blank=True, null=True)