from django.views.generic import TemplateView
from ..models import AppModule, Duration, UserWindow, AppCost


class PlansList(TemplateView):
    template_name = "companies/pricing.html"

    def get_context_data(self, **kwargs):
        plans = AppModule.objects.all().values('id', 'name', 'description')
        plans = list(plans)
        context = {'plans': plans}
        return context
