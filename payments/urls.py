from django.urls import path

from payments.views import paymentPage, paymentCharge, chargeList, addRequest,checkName

urlpatterns = [
    path('pay', paymentPage, name='Payment Page'),
    path('callback', paymentCharge, name='Payment CallBack'),
    path('payments', chargeList, name='Payment List'),
    path('add-request', addRequest, name='Add Request'),
    path('check-name', checkName, name='Check Name'),
    
]