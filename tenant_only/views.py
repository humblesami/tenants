from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "customers/index.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context