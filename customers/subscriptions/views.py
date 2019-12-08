import uuid

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
from customers.model_files.payemts import Payment, PaymentMethod, PaymentInProgress
from main_app.ws_methods import add_interval, produce_exception

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_payment_data(token):
    payment_in_progress = PaymentInProgress.objects.get(token=token)
    plan = payment_in_progress.plan.__dict__
    payment_in_progress = PaymentInProgress.objects.filter(token=token)
    payment_in_progress = payment_in_progress.values('transaction_id', 'amount', 'email', 'company', 'method_id')
    payment_in_progress = payment_in_progress[0]
    return plan, payment_in_progress

def validate_payment_data(req_data):
    company = req_data['company']
    password = req_data['password']
    amount = req_data['amountpay']
    error = ''
    already = Client.objects.filter(schema_name=company)
    if already:
        message = 'Company Already Exists'
        if error:
            error += ', ' + message
    if not amount or not password:
        message = 'Please provide all the fields'
        if error:
            error += ', ' + message
    return error, company, password, amount

def subscribe(request, plan_id, token=None):
    template_name = 'customers/subscribe.html'
    email = ''
    amount = 0
    company = ''
    password = ''

    plan = None
    method_id = 0
    context = None
    payment_response = None
    payment_in_progress = None
    req_data = request.POST
    req_data = req_data.dict()

    if token:
        plan, payment_in_progress = get_payment_data(token)
    elif req_data.get('token'):
        token = req_data['token']
        plan, payment_in_progress = get_payment_data(token)
        req_data['company'] = payment_in_progress['company']
    else:
        qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
        plan = list(qs)[0]

    if request.method != 'POST':
        plan['cents_cost'] = int(plan['cost']) * 100
        context = {
            'key': settings.STRIPE_PUBLISHABLE_KEY,
            'plan': plan,
            'error': ''
        }
        if token:
            context['token'] = token
        if payment_in_progress:
            context['company'] = payment_in_progress['company']
        return render(request, template_name, context)
    else:
        req_data['key'] = settings.STRIPE_PUBLISHABLE_KEY
        req_data['plan'] = plan
        context = req_data
        if token:
            context['token'] = token
        try:
            if token:
                email = payment_in_progress['email']
                amount = payment_in_progress['amount']
                company = payment_in_progress['company']
                method_id = payment_in_progress['method_id']
                transaction_id = payment_in_progress['transaction_id']
                password = req_data['password']
                context['token'] = token
            else:
                error, company, password, amount = validate_payment_data(req_data)
                if error:
                    context['error'] = error
                    return render(request, template_name, context)

                amount = req_data['amountpay']
                amount = int(amount) / 100
                res = make_payment(req_data, amount)
                error = res['error']
                if error:
                    context['error'] = error
                    return render(request, template_name, context)
                try:
                    context['token'] = token = res['token']
                    method_id = res['method_id']
                    payment_response = res['payment_response']
                    payment_in_progress = res['payment_in_progress']
                    transaction_id = payment_response['transaction_id']
                    email = payment_response['billing_details']['name']
                except:
                    res = produce_exception()
                    context['error'] = res
                    return render(request, template_name, context)

            payment = Payment.objects.create(transaction_id=transaction_id, method_id=method_id, amount=amount)
            plan_cost = PlanCost.objects.filter(plan_id=plan['id']).last()
            subscription = Subscription(payment_id=payment.id, plan_id=plan['id'], plan_cost_id=plan_cost.id)
            subscription.amount = plan_cost.cost
            subscription.end_date = ws_methods.add_interval('days', plan['days'])
            res = create_tenant(company, email, password, subscription.id, request)
            if res != 'done':
                payment_in_progress.delete()
            else:
                context['error'] = res
                return render(request, template_name, context)
        except:
            res = produce_exception()
            context['error'] = res
            return render(request, template_name, context)


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



def make_payment(req_data, amount):
    token = uuid.uuid4().hex[:20]
    medium = PaymentMethod.objects.filter(name='Stripe')
    if not medium:
        medium = PaymentMethod.objects.create(name='Stripe')
    else:
        medium = medium[0]
    method_id = medium.id
    company = req_data['company']
    obj = PaymentInProgress.objects.create(method_id=method_id, plan_id=req_data['plan']['id'], company=company, token=token, amount=amount)
    payment_in_progress = obj
    payment_response = None
    charge = None
    amount = int(amount)
    error = ''
    try:
        token = req_data['stripeToken']
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Plan Scubscription',
            source=token,
            capture=True)
        payment_response = charge
        failure_code = payment_response['failure_code']
        if failure_code:
            payment_in_progress.delete()
            message = payment_response['failure_message']
            if error:
                message += ', ' + message
            error = message
        else:
            email = payment_response['billing_details']['name']
            payment_in_progress.transaction_id = payment_response['id']
            payment_in_progress.email = email
            payment_in_progress.save()

    except:
        payment_in_progress.delete()
        error = produce_exception()
    res = {'error':  error, 'method_id':  method_id, 'payment_response': payment_response, 'payment_in_progress': payment_in_progress }
    return res