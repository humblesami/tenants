import uuid
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django_tenants.utils import get_tenant_model
from django.contrib.contenttypes.models import ContentType

from authsignup.models import AuthUser
from py_utils.helpers import LogUtils, DateUtils
from ..models import ClientTenant
from ..plans.plan_models import Plan, PlanCost
from ..subscriptions.subscription_models import Subscription
from ..payments.payment_models import Payment, PaymentMethod, PaymentInProgress


stripe.api_key = settings.STRIPE_SECRET_KEY


def subscription_form(request, plan_id, token=None):
    template_name = 'companies/subscription/form.html'
    if request.method == 'POST':
        return post_subscription(request)
    context = get_response(plan_id, '', token)
    return render(request, template_name, context)


def get_response(plan_id, error='', token=None):
    qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
    plan = list(qs)[0]
    plan['cents_cost'] = int(plan['cost']) * 100
    context = {
        'plan': plan,
        'token': token,
        'error': error
    }
    if token:
        payment_in_progress_obj = PaymentInProgress.objects.get(token=token)
        payment_in_progress = payment_in_progress_obj.__dict__
        context['payment'] = payment_in_progress
        if not payment_in_progress.get('transactions_id'):
            context['key'] = settings.STRIPE_PUBLISHABLE_KEY
    else:
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
    return context


def check_sub_domain(request):
    sub_domain = request.GET['sub_domain']
    res = check_schema_name(sub_domain)
    return HttpResponse(res)


def check_schema_name(sub_domain, payment_token=None):
    existing = ClientTenant.objects.filter(schema_name=sub_domain)
    if existing:
        return 'Sub domain "'+sub_domain+'" has been already taken'
    else:
        existing = PaymentInProgress.objects.filter(company=sub_domain)
        if existing:
            existing = existing[0]
            if existing.token != payment_token:
                return 'Sub domain "' + sub_domain + '" has been already taken'
            else:
                return 'ok'
    return 'ok'


def post_subscription(request, payment_token=None):
    template_name = 'companies/subscription/form.html'
    req_url_postfix = ''
    try:
        req_data = request.POST
        res = check_schema_name(req_data['sub_domain'], payment_token)
        if res != 'ok':
            context = get_response(req_data['plan_id'], res, payment_token)
            return render(request, template_name, context)

        obj = PaymentInProgress(company=req_data['sub_domain'], plan_id=req_data['plan_id'])
        payment_token = uuid.uuid4().hex[:20]
        obj.amount=req_data['amount']
        obj.token = payment_token
        obj.save()

        payment_promise_obj = obj
        req_url_postfix += '/' + req_data['plan_id'] + '/' + payment_token

        res = make_payment(req_data, payment_promise_obj)
        if res != 'done':
            context = get_response(req_data['plan_id'], res, payment_token)
            return render(request, template_name, context)
        else:
            payment_promise = payment_promise_obj.__dict__
            req_url_postfix += '/' + payment_token
            with transaction.atomic():
                subscription_id = create_related_entries(req_data, payment_promise)
                print('creating tenant')
                res = create_tenant(payment_promise['email'], subscription_id, request)
            return redirect('/')
    except:
        res = LogUtils.get_error_message()
        context = get_response(req_data['plan_id'], res, payment_token)
        return render(request, template_name, context)


def make_payment(req_data, promise_obj):
    charge = stripe.Charge.create(
        amount=req_data['amount'],
        currency='usd',
        description='Plan Subscription',
        source=req_data['stripeToken'],
        capture=True)
    payment_response = charge
    if payment_response['failure_code']:
        payment_response['failure_message']
    else:
        on_payment_success(payment_response, promise_obj)
        return 'done'


def on_payment_success(payment_response, obj):
    email = payment_response['billing_details']['name']
    medium = PaymentMethod.objects.filter(name='Stripe')
    if not medium:
        medium = PaymentMethod.objects.create(name='Stripe')
    else:
        medium = medium[0]
    method_id = medium.id
    obj.transaction_id = payment_response['id']
    obj.email = email
    obj.error = ''
    obj.method_id = method_id
    obj.save()


def create_related_entries(req_data, payment_promise):
    plan_id = req_data['plan_id']
    amount = req_data['amount']
    transaction_id = payment_promise['transaction_id']
    method_id = payment_promise['method_id']

    plan_cost = PlanCost.objects.filter(plan_id=plan_id).values('id', 'cost', 'days')
    plan_cost = plan_cost[len(plan_cost) - 1]
    subscription = Subscription(plan_id=plan_id, plan_cost_id=plan_cost['id'])
    subscription.amount = plan_cost['cost']
    end_date = DateUtils.add_interval('days', plan_cost['days'])
    subscription.end_date = end_date
    subscription.save()

    obj = Payment(subscription_id=subscription.id, transaction_id=transaction_id)
    obj.method_id = method_id
    obj.amount = amount
    obj.save()
    return subscription.id


def create_tenant(email, subscription_id, request):
    res = 'Unknown issue'
    req_data = request.POST
    sub_domain = req_data['sub_domain']
    company = req_data['company']
    password = req_data['password']
    plan_id = req_data['plan_id']
    public_tenant = request.tenant
    try:
        tenant_model = get_tenant_model()
        with transaction.atomic():
            if not tenant_model.objects.filter(schema_name=sub_domain):

                schema_owner = User.objects.create(username='owner@'+sub_domain+'.com')
                schema_owner.save()

                domain_name = sub_domain + '.' + settings.server_domain
                company = tenant_model(schema_name=sub_domain, name=company, owner_id=schema_owner.id, domain_name=domain_name)
                company.subscription_id = subscription_id
                company.plan_id = plan_id
                company.save()

                create_public_user(company, email, password)

                request.tenant = company
                connection.set_tenant(request.tenant, False)
                ContentType.objects.clear_cache()
                try:
                    tenant_user = AuthUser(username=email, is_superuser=True, is_staff=True, is_active=True)
                    tenant_user.on_schema_creating = True
                    tenant_user.email = email
                    tenant_user.save()
                    tenant_user.set_password(password)
                    tenant_user.save()
                    print('\n\n\n Success while creating user\n\n\n')
                except:
                    print('\n\n\n Error while creating user\n\n\n')
                res = 'done'
            else:
                res = 'cusomer with name "' + sub_domain + '" already exists'
    except:
        res = LogUtils.get_error_message()
    request.tenant = public_tenant
    connection.set_tenant(request.tenant, False)
    ContentType.objects.clear_cache()
    return res


def create_public_user(email, password):
    public_user = User.objects.filter(email=email).firs()
    if not public_user:
        public_user = User.objects.create(email=email, username=email, is_active=True)
        public_user.set_password(password)
        public_user.save()
    else:
        raise Exception('User already exists with email '+email)