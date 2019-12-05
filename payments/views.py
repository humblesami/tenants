import stripe
from django.shortcuts import render
from main_app import settings
from customers.model_files.plans import PlanRequest
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.http import JsonResponse

def paymentPage(request):
    context = {
        'key': settings.STRIPE_PUBLISHABLE_KEY,        
    }
    return render(request, 'payments/new.html', context)

def paymentCharge(request): # new
    request1 = request
    if request.method == 'POST':
        amount = request.POST['amountpay']
        token = request.POST['stripeToken']
        paypaymentnow = chargePayment(amount,'usd','Odufax payment recieve',token)
        chargeId = paypaymentnow['id']

        request.session['chargeId'] = chargeId
        amountInt = int(amount)
        request.session['billAmount'] = amountInt
        context = {
            'amount' : amountInt,
            'user' : paypaymentnow['name']
        }
        return render(request, 'payments/callback.html',context)

def chargePayment(amount, currency, description, token):
    charge = stripe.Charge.create(
        amount=amount,
        currency=currency,
        description=description,
        source=token,
        capture=True,
    )
    charge_results = {"id" : charge.id , "name": charge['billing_details']['name'] }
    return charge_results

def chargeList(request):
    details = {}
    total_users = stripe.Charge.list()
    context = total_users.data
    i = 0
    for item in context:
        name = item['billing_details']['name']
        amount = item['amount']
        currency = item['currency']
        status = item['status']
        details[i] = {'name':name ,'amount':amount, 'currency': currency, 'status': status}
        i = i + 1

    return render(request, 'payments/list.html' , {'list': details})

# from rest_framework.decorators import api_view
# @api_view(['GET'])
# def addRequest(request):
#     name = request.GET['name']
#     email = request.GET['email']
#     obj = PlanRequest.objects.filter(name=name)
#     if(obj):
#         res = { 'error': 'User already Exist' }
#         return JsonResponse(res)
#     request_obj = PlanRequest(name=name,email=email,plan_id = 1)
#     request_obj.save()
#     res = { 'is': 'done' }
#     return JsonResponse(res)

# def checkName(request):
#     name = request.GET['name']
#     obj = PlanRequest.objects.filter(name = name)
#     result = {}
#     if obj:
#         result = { 'data' : obj.count() }
#     else:
#         result = { 'data' : "Done" }
#     return JsonResponse(result)