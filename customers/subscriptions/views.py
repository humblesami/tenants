import uuid
import urllib
import stripe
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django.core.management import call_command
from django_tenants.utils import get_tenant_model
from django.contrib.contenttypes.models import ContentType



from mainapp import settings, ws_methods
from mainapp.settings import TENANT_DOMAIN
from mainapp.ws_methods import produce_exception

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


def form_company_info(request, plan_id):
    try:
        template_name = 'customers/subscription/company_form.html'
        qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
        plan = list(qs)[0]
        plan['cents_cost'] = int(plan['cost']) * 100
        context = {
            'plan': plan,
        }
        if request.method != 'POST':
            return render(request, template_name, context)
        else:
            req_data = request.POST
            company = req_data['company']
            usd_amount = req_data['usd_amount']
            error = ''
            already = Client.objects.filter(schema_name=company)
            if already:
                message = 'Company Already Exists'
                if error:
                    error += ', ' + message
            if not usd_amount:
                message = 'Please provide all the fields'
                if error:
                    error += ', ' + message
            if error:
                return redirect('/subscriptions/' + req_data['plan_id'])
            else:
                payment_token = uuid.uuid4().hex[:20]
                medium = PaymentMethod.objects.filter(name='Stripe')
                if not medium:
                    medium = PaymentMethod.objects.create(name='Stripe')
                else:
                    medium = medium[0]
                method_id = medium.id
                obj = PaymentInProgress(method_id=method_id, plan_id=req_data['plan_id'])
                obj.company = company
                obj.token = payment_token
                obj.amount = usd_amount
                obj.save()
                success_url = 'payment/' + payment_token
                print('\n\n' + success_url + '\n\n')
                return redirect(success_url)
    except:
        res = produce_exception()
        context['error'] = res
        return render(request, template_name, context)


def form_payment(request, req_token):
    payment_in_progress_obj = PaymentInProgress.objects.get(token=req_token)
    plan_id = payment_in_progress_obj.plan_id
    qs = Plan.objects.filter(id=plan_id).values('id', 'name', 'cost', 'days')
    plan = list(qs)[0]
    plan['cents_cost'] = int(plan['cost']) * 100
    error = payment_in_progress_obj.error
    template_name = 'customers/subscription/payment_form.html'
    context = {
        'token': req_token,
        'error': error,
        'plan': plan,
        'key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, template_name, context)


def post_payment(request, req_token):
    payment_in_progress_obj = PaymentInProgress.objects.get(token=req_token)
    try:
        req_data = request.POST
        stripe_token = req_data['stripeToken']
        amount = payment_in_progress_obj.amount * 100
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Plan Subscription',
            source=stripe_token,
            capture=True)
        payment_response = charge
        print(charge)
        failure_code = payment_response['failure_code']
        if failure_code:
            error = payment_response['failure_message']
            payment_in_progress_obj.error = error
            return redirect('/subscriptions/payment/' + req_token)
        else:
            email = payment_response['billing_details']['name']
            payment_in_progress_obj.transaction_id = payment_response['id']
            payment_in_progress_obj.email = email
            payment_in_progress_obj.save()
            return redirect('/subscriptions/create/' + req_token)
    except:
        payment_in_progress_obj.error = error
        return redirect('/subscriptions/payment/' + req_token)


def form_subscription(request, req_token):
    template_name = 'customers/subscription_form.html'
    payment_in_progress_obj = PaymentInProgress.objects.get(token=req_token)
    payment_in_progress = payment_in_progress_obj.__dict__
    return render(request, template_name, payment_in_progress)


def post_subscription(request, req_token):
    try:
        payment_in_progress_obj = PaymentInProgress.objects.get(token=req_token)
        payment_in_progress = payment_in_progress_obj.__dict__
        plan_id = payment_in_progress['plan_id']
        method_id = payment_in_progress['method_id']
        transaction_id = payment_in_progress['transaction_id']
        email = payment_in_progress['email']
        amount = payment_in_progress['amount']
        password = request.POST['password']

        company = payment_in_progress['company']
        with transaction.atomic():
            plan_cost = PlanCost.objects.filter(plan_id=plan_id).values('id', 'cost', 'days')
            plan_cost = plan_cost[len(plan_cost) - 1]
            subscription = Subscription(plan_id=plan_id, plan_cost_id=plan_cost['id'])
            subscription.amount = plan_cost['cost']
            end_date = ws_methods.add_interval('days', plan_cost['days'])
            subscription.end_date = end_date
            subscription.save()

            obj = Payment(subscription_id=subscription.id, transaction_id=transaction_id)
            obj.method_id = method_id
            obj.amount = amount
            obj.save()
            print('creating tenant')
            res = create_tenant(company, email, password, subscription.id, plan_id, request)

        if res == 'done':
            payment_in_progress_obj.delete()
            return redirect('/')
        else:
            payment_in_progress_obj.error = res
            payment_in_progress_obj.save()
            return redirect('/subscriptions/create/'+req_token)
    except:
        payment_in_progress_obj.error = res
        payment_in_progress_obj.save()
        return redirect('/subscriptions/create/' + req_token)


def create_public_user(user_tenant, email, password):
    public_user = User.objects.filter(email=email)
    if not public_user:
        public_user = User.objects.create(email=email, username=email, is_active=True)
        public_user.set_password(password)
        public_user.save()
    else:
        public_user = public_user [0]
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

                # tenant_user = AuthUser(username=email, is_superuser=True, is_staff=True, is_active=True)
                # tenant_user.on_schema_creating = True
                # tenant_user.email = email
                # tenant_user.save()
                # tenant_user.set_password(password)
                # tenant_user.save()

                call_command('loaddata', 'website/fixtures/data.json')
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