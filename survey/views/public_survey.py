from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.db.models import Count
from survey.forms import ResponseForm
from survey.models import Category, Survey, Answer
from ast import literal_eval



class PublicSurvey:
    def get(self, request, *args, **kwargs):
        pass
    

    def post(self, request, *args, **kwargs):
        pass