import stripe
from main_app import settings
from django.views.generic import TemplateView
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymetCallback(TemplateView):
    template_name = 'payments/callback.html'
    def get_context_data(self, **kwargs):
        request = self.request
        req_data = request.POST
        if request.method == 'GET':
            req_data = request.GET
        amount = req_data['amountpay']
        token = req_data['stripeToken']
        paypaymentnow = make_payemt(amount,'usd','Odufax payment recieve',token)
        chargeId = paypaymentnow['id']

        request.session['chargeId'] = chargeId
        amountInt = int(amount)
        request.session['billAmount'] = amountInt
        context = {
            'amount' : amountInt,
            'user' : paypaymentnow['name']
        }
        return context


def make_payemt(amount, currency, description, token):
    charge = stripe.Charge.create(
        amount=amount,
        currency=currency,
        description=description,
        source=token,
        capture=True,
    )
    charge_results = {"id" : charge.id , "name": charge['billing_details']['name'] }
    return charge_results


class PaymentList(TemplateView):
    template_name = 'payments/list.html'
    def get_context_data(self, **kwargs):
        details = {}
        total_users = stripe.Charge.list()
        payment_list = total_users.data
        i = 0
        for item in payment_list:
            name = item['billing_details']['name']
            amount = item['amount']
            currency = item['currency']
            status = item['status']
            details[i] = {'name':name ,'amount':amount, 'currency': currency, 'status': status}
            i = i + 1

        context = {'list': details}
        return context