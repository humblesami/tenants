from django.http import HttpResponse
from django.views.generic import TemplateView
from customers.model_files.plans import PlanRequest, Plan
from main_app import settings


class SubscriptionForm(TemplateView):
    template_name = 'payments/new.html'
    def get_context_data(self, plan_id, **kwargs):
        qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
        plan = list(qs)[0]
        context = {
            'key': settings.STRIPE_PUBLISHABLE_KEY,
            'plan': plan
        }
        return context


class SaveRequest(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        request = self.request
        res = 'Unknown'
        name = request.GET['name']
        email = request.GET['email']
        request_obj = PlanRequest(name=name, email=email, plan_id=1)
        request_obj.save()
        res = 'done'
        return HttpResponse(res)