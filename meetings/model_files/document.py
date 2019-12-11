from .event import Event
from .topic import Topic
from django.db import models
from mainapp import ws_methods
from documents.file import File
from django.db import transaction


class MeetingDocument(File):
    meeting = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='documents')

    def save(self, *args, **kwargs):
        if not self.file_type:
            self.file_type = 'meeting'
        super(MeetingDocument, self).save(*args, **kwargs)

    @classmethod
    def get_attachments(cls, request, params):
        parent_id = params.get('parent_id')
        docs = File.objects.filter(meeting_id=parent_id)
        docs = docs.values('id', 'name')
        docs = list(docs)
        return docs

    @property
    def breadcrumb(self):
        event_obj = self.meeting
        data = []
        if event_obj:
            if event_obj.exectime != 'ongoing':
                data.append({'title': event_obj.exectime, 'link': '/meetings/' + event_obj.exectime})
            data.append({'title': event_obj.name, 'link': '/meeting/' + str(event_obj.id)})
            return data

    def notification_text(self):
        doc_name = self.name
        if len(doc_name) > 20:
            doc_name = doc_name[:20] + '...'
        return ' Document "' + doc_name + '" in ' + self.meeting.notification_text()

    def get_audience(self):
        res = []
        for obj in self.meeting.attendees.all():
            res.append(obj.id)
        return res

    @classmethod
    def upload_meeting_documents(cls, request, params):
        attachments = params['attachments']
        meeting_id = params['meeting_id']
        meeting_docs = []
        with transaction.atomic():
            for attachment in attachments:
                file_name = attachment['name']
                doc_file = attachment['binary']
                doc_file = ws_methods.base64_str_to_file(doc_file, file_name)
                try:
                    file_name = attachment['file_name']
                except:
                    pass
                meeting_doc = MeetingDocument(
                    meeting_id=meeting_id,
                    file_type='meeting',
                    name=file_name,
                    attachment=doc_file
                )
                meeting_doc.save()
                meeting_doc = ws_methods.obj_to_dict(meeting_doc, 
                fields=[
                    'id', 
                    'name', 
                    'content', 
                    'file_ptr_id', 
                    'file_type', 
                    'html',
                    'meeting_id',
                    'pdf_doc'
                    ])
                meeting_docs.append(meeting_doc)
        if meeting_docs:        
            return meeting_docs
        else:
            return 'Something went wrong while uploading meeting documents'


class AgendaDocument(File):
    agenda = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='documents')

    @classmethod
    def get_attachments(cls, request, params):
        parent_id = params.get('parent_id')
        docs = File.objects.filter(agenda_id=parent_id)
        docs = docs.values('id', 'name')
        docs = list(docs)
        return docs

    def save(self, *args, **kwargs):
        if not self.file_type:
            self.file_type = 'topic'
        super(AgendaDocument, self).save(*args, **kwargs)

    def notification_text(self):
        doc_name = self.name
        if len(doc_name) > 20:
            doc_name = doc_name[:20] + '...'
        agenda_name = self.agenda.name
        if len(agenda_name) > 20:
            agenda_name = agenda_name[20] + '...'
        return ' Document "' + doc_name + '" in Agenda topic "'+ agenda_name + '" in ' + self.meeting.notification_text()

    @property
    def breadcrumb(self):
        topic_obj = self.agenda
        event_obj = topic_obj.event
        data = []
        if event_obj:
            if event_obj.exectime != 'ongoing':
                data.append({'title': event_obj.exectime, 'link': '/meetings/' + event_obj.exectime})
            data.append({'title': event_obj.name, 'link': '/meeting/' + str(event_obj.id)})
            if topic_obj:
                data.append({'title': topic_obj.name, 'link': '/topic/' + str(topic_obj.id)})
            return data
        

    def get_audience(self):
            res = []
            for obj in self.agenda.event.attendees.all():
                res.append(obj.id)
            return res

    
    @classmethod
    def upload_agenda_documents(cls, request, params):
        attachments = params['attachments']
        topic_id = params['topic_id']
        topic_docs = []
        with transaction.atomic():
            for attachment in attachments:
                file_name = attachment['name']
                doc_file = attachment['binary']
                doc_file = ws_methods.base64_str_to_file(doc_file, file_name)
                try:
                    file_name = attachment['file_name']
                except:
                    pass
                topic_doc = AgendaDocument(
                    agenda_id=topic_id,
                    file_type='topic',
                    name=file_name,
                    attachment=doc_file
                )
                topic_doc.save()
                topic_doc = ws_methods.obj_to_dict(topic_doc, 
                fields=[
                    'id', 
                    'name', 
                    'content', 
                    'file_ptr_id', 
                    'file_type', 
                    'html',
                    'meeting_id',
                    'pdf_doc'
                    ])
                topic_docs.append(topic_doc)
        if topic_docs:        
            return topic_docs
        else:
            return 'Something went wrong while uploading agenda documents'