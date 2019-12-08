import stripe
from django.contrib.auth.models import User

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django_tenants.utils import get_tenant_model
from django.contrib.contenttypes.models import ContentType

from customers.model_files.subscription import Subscription
from customers.models import Client
from main_app import settings, ws_methods
from main_app.settings import TENANT_DOMAIN
from customers.model_files.plans import Plan, PlanCost
from customers.model_files.payemts import Payment, PaymentMethod
from main_app.ws_methods import add_interval

stripe.api_key = settings.STRIPE_SECRET_KEY


def subscribe(request, plan_id):
    template_name = 'customers/subscribe.html'
    qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
    plan = list(qs)[0]
    if request.method != 'POST':
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
            payment_response = make_payemt(amount, 'usd', 'Payment Receive', token)
            failure_code = payment_response ['failure_code']
            if failure_code:
                message = payment_response['failure_message']
                if context['error']:
                    message += ', ' + message
                context['error'] = message
            else:
                email = payment_response['billing_details']['name']
        if context['error']:
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
            payment = Payment.objects.create(transaction_id=transaction_id, method_id=medium.id, amount=amount)
            plan_cost = PlanCost.objects.filter(plan_id=plan['id']).last()
            subscription = Subscription(payment_id=payment.id, plan_id=plan['id'], plan_cost_id=plan_cost.id)
            subscription.amount = plan_cost.cost
            subscription.end_date = add_interval('days', plan['days'])
            res = create_tenant(company, email, password, subscription.id, request)
            return redirect('/')


def create_tenant(t_name, email, password, subscription_id, request):
    res = 'Unknown issue'
    try:
        tenant_model = get_tenant_model()
        with transaction.atomic():
            if not tenant_model.objects.filter(schema_name=t_name):

                owner_mail = 'owner@'+t_name+'.com'
                owner = User.objects.create(username=owner_mail, email=owner_mail, is_active=True)
                owner.set_password(password)
                owner.save()

                tenant_superuser = User.objects.filter(email=email)
                if not tenant_superuser:
                    tenant_superuser = User.objects.create(username=email, email=email, is_active=True)
                    tenant_superuser.set_password(password)
                    tenant_superuser.save()
                else:
                    tenant_superuser = tenant_superuser[0]

                domain_url = t_name + '.' + TENANT_DOMAIN
                company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_url=domain_url)
                company.subscription_id = subscription_id
                company.save()

                company.plan_id = company.subscription.plan.id
                company.users.add(owner)
                company.users.add(tenant_superuser)
                company.save()

                request.tenant = company
                connection.set_tenant(request.tenant)
                ContentType.objects.clear_cache()

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
        capture=True,)
    return charge