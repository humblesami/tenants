from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django_tenants.utils import get_tenant_model

from customers.model_files.payemts import Payment, PaymentMethod
from customers.model_files.plans import PlanRequest, Plan
from customers.models import Client
from main_app import settings, ws_methods
import stripe

from main_app.settings import TENANT_DOMAIN

stripe.api_key = settings.STRIPE_SECRET_KEY


# class SubscriptionForm(TemplateView):
#     def get_context_data(self, **kwargs):
#         return {}
def subscribe(request, plan_id, request_id=None):
    template_name = 'payments/new.html'
    # def get_context_data(self, plan_id, **kwargs):
    if request.method != 'POST':
        qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
        plan = list(qs)[0]
        plan['cents_cost'] = int(plan['cost']) * 100
        context = {
            'key': settings.STRIPE_PUBLISHABLE_KEY,
            'plan': plan
        }
        return render(request, template_name, context)
    else:
        req_data = request.POST
        amount = req_data['amountpay']
        company = req_data['company']
        password = req_data['password']
        context = {'error': ''}

        already = Client.objects.filter(schema_name=company)
        if already:
            message = 'Company Already Exists'
            if context['error']:
                message += ', '+message
            context['error'] = message
        if not amount or not password:
            message = 'Please provide all the fields'
            if context['error']:
                message += ', ' + message
            context['error'] = message
            return render(request, template_name, )
        email = ''
        payment_response = None
        if not context['error']:
            token = req_data['stripeToken']
            payment_response = make_payemt(amount, 'usd','Odufax payment recieve',token)
            failure_code = payment_response ['failure_code']
            if failure_code:
                message = payment_response['failure_message']
                if context['error']:
                    message += ', ' + message
                context['error'] = message
            else:
                email = payment_response['billing_details']['name']
        if not email:
            message = 'Email not found'
            if context['error']:
                message += ', ' + message
            context['error'] = message
        if context['error']:
            qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
            plan = list(qs)[0]
            plan['cents_cost'] = int(plan['cost']) * 100
            context = {
                'key': settings.STRIPE_PUBLISHABLE_KEY,
                'plan': plan,
                'error': context['error']
            }
            return render(request, template_name, context)
        else:
            transaction_id = payment_response['id']
            medium = PaymentMethod.objects.filter(name='Stripe')
            if not medium:
                medium = PaymentMethod.objects.create(name='Stripe')
            else:
                medium = medium[0]

            obj = Payment(transaction_id=transaction_id, medium_id=medium.id, amount=amount)
            obj.save()
            res = create_tenant(company, email, password, request)
            return redirect('/')


def create_tenant(t_name, email, password, request):
    res = 'Unknown issue'
    try:
        tenant_model = get_tenant_model()
        with transaction.atomic():
            if not tenant_model.objects.filter(schema_name=t_name):

                user_exists = User.objects.filter(email=email)
                if not user_exists:
                    owner = User.objects.create(username=email, email=email, is_active=True)
                    owner.set_password(password)
                    owner.save()

                domain_url = t_name + '.' + TENANT_DOMAIN
                company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_url=domain_url)
                company.save()
                company.users.add(owner)

                request.tenant = company
                connection.set_tenant(request.tenant)
                ContentType.objects.clear_cache()

                if not user_exists:
                    owner = User.objects.create(username=email, email=email, is_superuser=True, is_staff=True, is_active=True)
                    owner.set_password(password)
                    owner.save()

                company = tenant_model.objects.get(schema_name='public')
                request.tenant = company
                connection.set_tenant(request.tenant)
                ContentType.objects.clear_cache()

                res = 'done'
            else:
                res = 'Client with id' + t_name + ' already exists'
    except:
        res = ws_methods.produce_exception()
    return res



def make_payemt(amount, currency, description, token):
    charge = stripe.Charge.create(
        amount=amount,
        currency=currency,
        description=description,
        source=token,
        capture=True,
    )
    return charge


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