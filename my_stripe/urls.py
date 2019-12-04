from django.urls import path

from my_stripe.views import paymentPage, paymentCharge, chargeList

urlpatterns = [
    path('pay', paymentPage, name='Payment Page'),
    path('callback', paymentCharge, name='Payment CallBack'),
    path('payments', chargeList, name='Payment List'),
]