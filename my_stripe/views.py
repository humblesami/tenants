import stripe
from django.shortcuts import render
from tenant_tutorial import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


def paymentPage(request):
    attachment = request.session.get('attachment')
    # print("filess: ",attachment)
    # pages = len(attachment)
    # print("pages: ", pages)
    # amount = BillCalculator(pages)
    amount = 8000
    amountforView = (amount/100)
    amountforJS = amount
    # attachments = attachment

    context = {
        'key': settings.STRIPE_PUBLISHABLE_KEY,
        'amount': amountforView,
        'amount_js' : amountforJS,
        # 'attachments': attachments
    }

    return render(request,'stripe/paymentpage.html',context)

def paymentCharge(request): # new
    request1 = request
    if request.method == 'POST':
        amount = request.POST['amountpay']
        token = request.POST['stripeToken']
        # attachments = request.POST['attachments']
        # print("paymentChargePage: ",attachments)
        paypaymentnow = chargePayment(amount,'usd','Odufax payment recieve',token)
        chargeId = paypaymentnow['id']

        request.session['chargeId'] = chargeId
        amountInt = int(amount)
        amountforJS = (amountInt/100)
        request.session['billAmount'] = amountforJS
        context = {
            'amount' : amountforJS,
            'user' : paypaymentnow['name']
            # 'attachments': attachments,
        }
        return render(request, 'stripe/charge.html',context)

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

    return render(request, 'stripe/paymentlist.html' , {'list': details})