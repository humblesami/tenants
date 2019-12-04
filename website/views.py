from django.shortcuts import render
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context