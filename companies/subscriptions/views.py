import uuid
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from sam_pytools import LogUtils, DateUtils
from ..models import ClientTenant, Subscription, Payment, PaymentMethod, AppCost

stripe.api_key = settings.STRIPE_SECRET_KEY


def subscription_form(request, plan_id, token=None):
    template_name = 'companies/subscription/form.html'
    if request.method == 'POST':
        return post_subscription(request)
    context = get_response(plan_id, '', token)
    return render(request, template_name, context)


def get_response(plan_id, error='', token=None):
    qs = Subscription.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
    plan = list(qs)[0]
    plan['cents_cost'] = int(plan['cost']) * 100
    context = {
        'plan': plan,
        'token': token,
        'error': error
    }
    if token:
        payment_in_progress_obj = Payment.objects.get(token=token)
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
        existing = Payment.objects.filter(company=sub_domain)
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

        obj = Payment(company=req_data['sub_domain'], plan_id=req_data['plan_id'])
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
            req_url_postfix += '/' + payment_token
            return redirect('/')
    except:
        res = LogUtils.get_error_message()
        context = get_response(req_data['plan_id'], res, payment_token)
        return render(request, template_name, context)


def make_payment(req_data, promise_obj):
    charge = stripe.Charge.create(
        amount=req_data['amount'],
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
