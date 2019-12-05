from django.urls import path

from payments.views import paymentPage, paymentCharge, chargeList

urlpatterns = [
    path('new', paymentPage, name='Payment Page'),
    path('callback', paymentCharge, name='Payment CallBack'),
    path('list', chargeList, name='Payment List'),
]