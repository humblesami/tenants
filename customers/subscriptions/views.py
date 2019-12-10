import uuid
import urllib
import stripe
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django_tenants.utils import get_tenant_model
from django.contrib.contenttypes.models import ContentType

from auth_t.models import TenantUser

from main_app import settings, ws_methods
from main_app.settings import TENANT_DOMAIN
from main_app.ws_methods import produce_exception

from customers.models import Client
from customers.model_files.plans import Plan, PlanCost
from customers.model_files.subscription import Subscription
from customers.model_files.payemts import Payment, PaymentMethod, PaymentInProgress

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_payment_data(token):
    payment_in_progress = PaymentInProgress.objects.get(token=token)
    plan = payment_in_progress.plan.__dict__
    payment_in_progress = PaymentInProgress.objects.get(token=token)
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
    return error, company, password

def subscribe(request, plan_id, req_token=None, error=None):
    template_name = 'customers/subscribe.html'

    token = None
    req_data = request.POST
    req_data = req_data.dict()
    payment_in_progress_obj = None
    payment_in_progress_dict = None

    if req_token:
        token = req_token
        plan, payment_in_progress_obj = get_payment_data(req_token)
        payment_in_progress_dict = payment_in_progress_obj.__dict__
    elif req_data.get('token'):
        token = req_data['token']
        plan, payment_in_progress_obj = get_payment_data(token)
        payment_in_progress_dict = payment_in_progress_obj.__dict__
        req_data['company'] = payment_in_progress_dict['company']
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
        if payment_in_progress_dict and payment_in_progress_dict['error']:
            context['error'] = payment_in_progress_dict['error']
        elif error:
            context['error'] = error
        if payment_in_progress_dict:
            context['company'] = payment_in_progress_dict['company']
        return render(request, template_name, context)
    else:
        req_data['key'] = settings.STRIPE_PUBLISHABLE_KEY
        req_data['plan'] = plan
        context = req_data
        if token:
            context['token'] = token
        try:
            print('Starting')
            if token:
                email = payment_in_progress_dict['email']
                usd_amount = payment_in_progress_dict['amount']
                company = payment_in_progress_dict['company']
                method_id = payment_in_progress_dict['method_id']
                transaction_id = payment_in_progress_dict['transaction_id']
                password = req_data['password']
                context['token'] = token
            else:
                error, company, password = validate_payment_data(req_data)
                if error:
                    context['error'] = error
                    return render(request, template_name, context)

                print('validated')
                cent_amount = req_data['amountpay']
                cent_amount = int(cent_amount)
                usd_amount = int(cent_amount) / 100
                res = make_payment(req_data, cent_amount, usd_amount)
                print('payment tried')
                if not res.get('paid') and res.get('error'):
                    return render(request, template_name, res)

                payment_in_progress_obj = res['payment_in_progress']
                error = res['error']
                method_id = res['method_id']
                payment_response = res['payment_response']
                email = payment_response['billing_details']['name']
                token = context['token'] = res['token']
                transaction_id = payment_response['id']
                if error:
                    print('payment failed')
                    return send_error(error, context, req_token, token, template_name, request, payment_in_progress_obj)
                print('payment succeeded')
            if not transaction_id:
                print('payment failed no transaction id')
                res = 'Invalid transaction id'
                return send_error(res, context, req_token, token, template_name, request, payment_in_progress_obj)
            with transaction.atomic():
                plan_cost = PlanCost.objects.filter(plan_id=plan['id']).values('id', 'cost', 'days')
                plan_cost = plan_cost[len(plan_cost) - 1]
                subscription = Subscription(plan_id=plan['id'], plan_cost_id=plan_cost['id'])
                subscription.amount = plan_cost['cost']
                end_date = ws_methods.add_interval('days', plan_cost['days'])
                subscription.end_date = end_date
                subscription.save()

                obj = Payment(subscription_id=subscription.id, transaction_id=transaction_id)
                obj.method_id = method_id
                obj.amount = usd_amount
                obj.save()
                print('creating tenant')
                res = create_tenant(company, email, password, subscription.id, plan['id'], request)

            if res == 'done':
                payment_in_progress_obj.delete()
                return redirect('/')
            else:
                return send_error(res, context, req_token, token, template_name, request, payment_in_progress_obj)
        except:
            res = produce_exception()
            return send_error(res, context, req_token, token, template_name, request, payment_in_progress_obj)


def send_error(res, context, req_token, token, template_name, request, payment_in_progress_obj):
    error = res
    context['error'] = error
    try:
        payment_in_progress_obj.error = error
        payment_in_progress_obj.save()
    except:
        new_error = produce_exception()
        pass
    if not req_token and token:
        path = urllib.parse.urljoin(request.path, token)
        return redirect(path)
    else:
        return render(request, template_name, context)


def create_public_user(user_tenant, email, password):
    public_user = User.objects.filter(email=email)
    if not public_user:
        public_user = User.objects.create(email=email, username=email, is_active=True)
        public_user.set_password(password)
        public_user.save()
    user_tenant.users.add(public_user)
    user_tenant.save()


def create_tenant(t_name, email, password, subscription_id, plan_id, request):
    res = 'Unknown issue'
    public_tenant = request.tenant
    try:
        tenant_model = get_tenant_model()
        with transaction.atomic():
            if not tenant_model.objects.filter(schema_name=t_name):

                schema_owner = User.objects.create(username='owner@'+t_name+'.com')
                schema_owner.save()

                domain_url = t_name + '.' + TENANT_DOMAIN
                company = tenant_model(schema_name=t_name, name=t_name, owner_id=schema_owner.id, domain_url=domain_url)
                company.subscription_id = subscription_id
                company.plan_id = plan_id
                company.save()

                create_public_user(company, email, password)

                request.tenant = company
                connection.set_tenant(request.tenant, False)
                ContentType.objects.clear_cache()

                # all the rest is handled in tenant user creation
                tenant_user = TenantUser(username=email, is_superuser=True, is_staff=True, is_active=True)
                tenant_user.on_schema_creating = True
                tenant_user.email = email
                tenant_user.save()
                tenant_user.set_password(password)
                tenant_user.save()
                res = 'done'
            else:
                res = 'Client with id' + t_name + ' already exists'
    except:
        res = ws_methods.produce_exception()
    request.tenant = public_tenant
    connection.set_tenant(request.tenant, False)
    ContentType.objects.clear_cache()
    return res


def make_payment(req_data, cent_amount, usd_amount):
    payment_token = uuid.uuid4().hex[:20]
    medium = PaymentMethod.objects.filter(name='Stripe')
    if not medium:
        medium = PaymentMethod.objects.create(name='Stripe')
    else:
        medium = medium[0]
    method_id = medium.id
    company = req_data['company']
    obj = PaymentInProgress(method_id=method_id, plan_id=req_data['plan']['id'], company=company, token=payment_token)
    obj.amount = usd_amount
    obj.save()
    payment_in_progress = obj
    payment_response = None
    charge = None
    error = ''
    paid = None
    try:
        stripe_token = req_data['stripeToken']
        charge = stripe.Charge.create(
            amount=cent_amount,
            currency='usd',
            description='Plan Scubscription',
            source=stripe_token,
            capture=True)
        payment_response = charge
        print(charge)
        failure_code = payment_response['failure_code']
        if failure_code:
            payment_in_progress.delete()
            message = payment_response['failure_message']
            if error:
                message += ', ' + message
            error = message
            return {'error' : error}
        else:
            paid = 1
            email = payment_response['billing_details']['name']
            payment_in_progress.transaction_id = payment_response['id']
            payment_in_progress.email = email
            payment_in_progress.save()
    except:
        error = produce_exception()
    res = {
        'error':  error,
        'paid': paid,
        'token': payment_token,
        'method_id':  method_id,
        'payment_response': payment_response,
        'payment_in_progress': payment_in_progress
    }
    return res