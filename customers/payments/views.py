import stripe
from main_app import settings
from django.views.generic import TemplateView
from customers.model_files.payemts import Payment


class PaymentListLocal(TemplateView):
    template_name = 'customers/payments.html'
    def get_context_data(self, **kwargs):
        details = {}
        total_users = stripe.Charge.list()
        payment_list = Payment.objects.all().values('amount',)
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


class PaymentList(TemplateView):
    template_name = 'customers/payments.html'
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