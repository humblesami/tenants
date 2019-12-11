from django import forms
from django.contrib import admin
from documents.admin import FileInlineAdmin, FileAdmin
from mainapp.admin import BaseAdmin, BaseInlineAdmin
from .models import *
import nested_admin


class VotingChoiceAdmin(BaseAdmin):
    autocomplete_fields = ['voting_type']


class ChoiceInline(BaseInlineAdmin):
    model = VotingChoice
    extra = 0


class VotingTypeAdmin(BaseAdmin):
    list_display = ['name']
    inlines = [ChoiceInline]
    list_filter = ['name']
    search_fields = ['name']
    

class VotingDocAdmin(FileAdmin):
    pass


class VotingDocInline(FileInlineAdmin):
    model = VotingDocument
    autocomplete_fields = ['voting']

class VotingForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = ()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meeting'].queryset = Event.objects.filter(archived=False)

class VotingAdmin(BaseAdmin):
    form = VotingForm
    # inlines = [VotingDocInline,]
    search_fields = ['name']
    fieldsets = [
        (None, {
            'fields': [
                'voting_type',
                'name',
                'description',
                'meeting',
                'topic',
                'respondents',
                'open_date',
                'close_date',
                'signature_required',
                'enable_discussion',
                'public_visibility',
                'is_published',
                ]})]
    autocomplete_fields = ['voting_type', 'respondents']
    change_form_template = 'admin/actions_change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("my_status",)
        form = super(VotingAdmin, self).get_form(request, obj, **kwargs)
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if self.has_change_permission(request):
            extra_context = extra_context or {}
            voting_id = request.resolver_match.kwargs['object_id']
            if voting_id:
                
                voting_choices = list(VotingChoice.objects.filter(voting_type = Voting.objects.get(pk=voting_id).voting_type.id))
                extra_context['option_data']=[]
                extra_context['option_results'] = []
                for option in voting_choices:
                    extra_context['option_data'].append({'id': option.id, 'name': option.name})
                    extra_context['option_results'].append({'option_name': option.name, 'option_result': 0, 'option_perc': 0})

                voting_results = list(VotingAnswer.objects.values('user_answer__name').annotate(answer_count=Count('user_answer')).filter(voting_id = voting_id))
                if voting_results:
                    total = 0
                    for result in voting_results:
                        total += result['answer_count']
                    for result in voting_results:
                        for extra_result in extra_context['option_results']:
                            if extra_result['option_name'] == result['user_answer__name']:
                                extra_result['option_result'] = result['answer_count']
                                extra_result['option_perc'] = round(((result['answer_count']/ total)*100),2)
                        # extra_context['option_results'].append({'option_name': result['answer__name'], 'option_result': result['answer_count'],
                        # 'option_perc': round(((result['answer_count']/ total)*100),2)})
                
                user_answer = VotingAnswer.objects.filter(voting_id=voting_id, user_id = request.user.id)
                # if not user_answer:

                return super(VotingAdmin, self).change_view(
                    request, object_id, form_url, extra_context=extra_context,)
                # else:
                #     return super(VotingAdmin, self).change_view(
                # request, object_id, form_url, extra_context=extra_context,)     
            else:
                return super(VotingAdmin, self).change_view(
                request, object_id, form_url, extra_context=extra_context,)
        else:
            extra_context = extra_context or {}
            return super(VotingAdmin, self).change_view(
                request, object_id, form_url, extra_context=extra_context,)


class VotingAnswerAdmin(BaseAdmin):
    list_display = ['user_answer', 'voting', 'user', 'signature_data']
    # list_filter = ['answer', 'user']
    list_filter = ['user']
    search_fields = ['user_answer__name', 'voting__name', 'user__username']


admin.site.register(Voting, VotingAdmin)
admin.site.register(VotingType, VotingTypeAdmin)
admin.site.register(VotingAnswer, VotingAnswerAdmin)
admin.site.register(VotingChoice, VotingChoiceAdmin)