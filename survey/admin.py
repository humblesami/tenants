# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError

from survey.models import Answer, Category, Question, Response, Survey
from meetings.model_files.event import Event
from .actions import make_published
from django.db import models
from django.forms import Textarea
import nested_admin
from mainapp.admin import BaseInlineAdmin, BaseAdmin


class QuestionInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass
        if count < 1:
            raise forms.ValidationError('You must have at least one question')


class QuestionInline(BaseInlineAdmin):
    formset = QuestionInlineFormset
    model = Question
    exclude = ('order', 'category', 'required', 'created_at', 'created_by', 'updated_at', 'updated_by')
    ordering = ["category", ]
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                        attrs={'rows': 2,
                                'cols': 10,})},
    }


class CategoryInline(BaseInlineAdmin):
    model = Category
    exclude = ['order', ]
    extra = 1


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ()

    def clean(self):
        respondents = self.cleaned_data.get('respondents')
        if not respondents:
            raise ValidationError("There must be at least one respondent, to save survey")

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meeting'].queryset = Event.objects.filter(archived=False)

class SurveyAdmin(BaseAdmin):
    form = SurveyForm
    list_display = ("name", "is_published", "need_logged_user")
    list_filter = ("is_published", "need_logged_user")
    autocomplete_fields = ['respondents']
    filter_horizontal = ('respondents',)
    inlines = [QuestionInline]
    actions = [make_published]
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
                'meeting',
                'topic',
                'respondents',
                'open_date',
                'close_date',
                'is_published',
                ]})]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                        attrs={'rows': 4,
                                'cols': 40,})},
    }
    change_form_template = "survey_custom_change_form.html"

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("template","need_logged_user","display_by_question", )
        form = super(SurveyAdmin, self).get_form(request, obj, **kwargs)
        return form


class AnswerBaseInline(admin.StackedInline):
    fields = ("question", "body")
    readonly_fields = ("question",)
    extra = 1
    model = Answer


class ResponseAdmin(BaseAdmin):
    list_display = ("interview_uuid", "survey", "created", "user")
    list_filter = ("survey", "created")
    date_hierarchy = "created"
    inlines = [AnswerBaseInline]
    # specifies the order as well as which fields to act on
    readonly_fields = ("survey", "created", "updated", "interview_uuid", "user")


# admin.site.register(Question, QuestionInline)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
