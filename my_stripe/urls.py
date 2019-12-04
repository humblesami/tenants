from django.urls import path

from my_stripe.views import paymentPage, paymentCharge, chargeList, addRequest,checkName

urlpatterns = [
    path('pay', paymentPage, name='Payment Page'),
    path('callback', paymentCharge, name='Payment CallBack'),
    path('payments', chargeList, name='Payment List'),
    path('addrequest', addRequest, name='Add Request'),
    path('checkname', checkName, name='Check Name'),
    
]