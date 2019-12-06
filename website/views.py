from django.shortcuts import render
from django.views.generic import TemplateView
from customers.model_files.plans import Plan


class Index(TemplateView):
    template_name = "website/index.html"
    def get_context_data(self, **kwargs):
        request = self.request
        print(6666)
        print(request.user.id)
        context = {}
        return context