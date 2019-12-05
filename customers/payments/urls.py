from django.urls import path
from .views import PaymetCallback, PaymentList

urlpatterns = [
    path('callback', PaymetCallback.as_view(), name='Payment CallBack'),
    path('list', PaymentList.as_view(), name='Payment List'),
]