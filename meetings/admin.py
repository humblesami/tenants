from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import is_password_usable, identify_hasher
from django.forms import PasswordInput
from django.utils.html import format_html
from django.contrib.auth.admin import GroupAdmin
from django.utils.decorators import method_decorator

from documents.admin import FileAdmin, FileInlineAdmin
from mainapp.admin import BaseAdmin, BaseInlineAdmin
from meetings.model_files.committee import Committee
from meetings.model_files.user import Profile
from django.views.decorators.debug import sensitive_post_parameters
from meetings.model_files.document import MeetingDocument, AgendaDocument
from .models import Event, Topic, News, NewsVideo, NewsDocument, InvitationResponse, LoginEntry
from django_currentuser.middleware import get_current_user
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
import nested_admin


class MeetingDocumentAdmin(FileAdmin):
    fields = ['name','attachment','meeting']


class MeetingDocInline(FileInlineAdmin):
    model = MeetingDocument


class NewsDocAdmin(FileAdmin):
    pass


class NewsDocumentInline(FileInlineAdmin):
    model = NewsDocument


class TopicDocInline(FileInlineAdmin):
    model = AgendaDocument


class TopicInline(BaseInlineAdmin):
    model = Topic
    # inlines = [TopicDocInline]
    extra = 0


class TopicAdmin(BaseAdmin):
    search_fields = ['name']
    # inlines = [TopicDocInline]


class EventAdmin(BaseAdmin):
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'start_date',
                'end_date',
                'attendees',
                'description',
                'pin',
                'conference_bridge_number',
                'video_call_link',
                'country',
                'state',
                'zip',
                'city',
                'street',
            ]
        })
    ]
    search_fields = ['name']
    autocomplete_fields = ['attendees']
    # autocomplete_fields = ('attendees',)

    # inlines = [TopicInline]
    # extra = 1
    readonly_fields = ('docs',)
    change_form_template = 'event_custom_change_form.html'

    def docs(self, obj):
        html = "<div>"
        for d in obj.meetingdocument_set.all():
            if d.pdf_doc:
                html += '<a title="%s" class="fa fa-4x fa-lg fa-file related-widget-wrapper-link change-related" href="%s"></a>' % (
                d.name, d.pdf_doc.url)
        html += '</div>'

        return format_html(html)


class UserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('email', 'password', 'first_name', 'last_name', 'mobile_phone', 'groups', 'two_factor_auth')
        widgets = {
            'password': PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['groups'].required = True

    def save(self, commit=True):
        password = self.instance.password
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        req_user = get_current_user()
        if req_user.is_superuser and password:
            has_valid_hash = False
            try:
                has_valid_hash = identify_hasher(password)
            except:
                pass
            if not has_valid_hash:
                user.set_password(password)
                user.save()
        return user

    def clean_email(self):
        if not self.instance.pk and Profile.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(u'This email already exists.')
        return self.cleaned_data['email']


class UserAdmin(BaseAdmin):
    search_fields = ('name',)
    autocomplete_fields = ['groups']
    form = UserForm
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'mobile_phone', 'two_factor_auth', 'is_superuser'
    )

    class Media:
        js = ('admin/js/profile_change_form.js',)

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            kwargs.update({'exclude': getattr(kwargs, 'exclude', tuple()) + ('two_factor_auth',), })
        if not request.user.is_superuser:
            kwargs.update({'exclude': getattr(kwargs, 'exclude', tuple()) + ('password',), })
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        return form


# class MeetingGroupAdmin(GroupAdmin):

#     def get_queryset(self, request):
#         # qs = super(GroupAdmin, self).get_queryset(request)
#         # qs = qs.filter(meetinggroup__app_label = "meetings")
#         qs = MeetingGroup.objects.filter()
#         return qs

#     def save_model(self, request, obj, form, change):
#         super(MeetingGroupAdmin, self).save_model(request, obj, form, change)


class CommitteeAdmin(BaseAdmin):
    autocomplete_fields = ['users']
    filter_horizontal = ('users',)
    fields = ('name', 'description', 'users')
    list_display = ('name', 'members')
    search_fields = ('name',)
    readonly_fields = ('members',)

    def members(self, obj):
        html = '<div>'
        for u in obj.users.all():
            if u.image:
                html += '<img title="%s" style="width:50px;border-radius:92px" src="/media/%s" />' % (
                u.username, u.image)
        html += '</div>'
        return format_html(html)
    members.short_description = ''


class NewsVideoInline(BaseInlineAdmin):
    model = NewsVideo
    extra = 0


class NewsAdmin(BaseAdmin):
    inlines = [NewsVideoInline]


class AttendeeAdmin(BaseAdmin):
    list_display = ('event', 'attendee', 'state', 'attendance')

class AgendaDocumentAdmin(BaseAdmin):
    fields = ['name','attachment']

admin.site.register(News, NewsAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(MeetingDocument, MeetingDocumentAdmin)
admin.site.register(AgendaDocument, AgendaDocumentAdmin)
admin.site.register(Profile, UserAdmin)
# admin.site.register(MeetingGroup, MeetingGroupAdmin)
admin.site.register(Committee, CommitteeAdmin)
admin.site.register(LoginEntry)
admin.site.register(InvitationResponse, AttendeeAdmin)
admin.site.site_header = "BoardSheet"
