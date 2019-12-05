from django.views.generic import TemplateView
from customers.model_files.plans import Plan


class PlansList(TemplateView):
    template_name = "plans/plan_list.html"

    def get_context_data(self, **kwargs):
        plans = Plan.objects.all().values('id', 'name', 'description', 'days', 'cost')
        plans = list(plans)
        context = {'plans': plans}
        return context


class PlanDetails(TemplateView):
    template_name = "plans/plan_detail.html"

    def get_context_data(self, plan_id, **kwargs):
        request = self.request
        plans = Plan.objects.filter(id=plan_id).values('id', 'name', 'description')
        plan_detail = list(plans)[0]
        context = {'plan': plan_detail }
        return context