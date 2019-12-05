from django.http import HttpResponse
from django.views.generic import TemplateView
from customers.model_files.plans import Plan, PlanRequest


class AddRequest(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        request = self.request
        res = 'Unknown'
        name = request.GET['name']
        email = request.GET['email']
        obj = PlanRequest.objects.filter(name=name)
        if obj:
            'User already Exist'
        else:
            request_obj = PlanRequest(name=name,email=email,plan_id = 1)
            request_obj.save()
            res = 'done'
        return HttpResponse(res)


class CheckName(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        res = 'Unknown'
        request = self.request
        name = request.GET['name']
        if not name:
            res = 'No name given'
        else:
            obj = PlanRequest.objects.filter(name = name)
            result = {}
            if obj:
                res = 'Already exists'
            else:
                res = 'done'
        return HttpResponse(res)


class PlanDetails(TemplateView):
    template_name = "website/plandetail.html"

    def get_context_data(self, id, request_id=None, **kwargs):
        request = self.request
        plan_amount = Plan.objects.filter(id = id)
        plan_amount = plan_amount[0]
        context = { 'plan':plan_amount }
        return context