from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "customers/index_tenant.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context