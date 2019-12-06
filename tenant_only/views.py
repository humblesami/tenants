from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "tenant_only/index.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context