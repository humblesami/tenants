from django.urls import path
from .views import PaymentListLocal, PaymentList

urlpatterns = [
    path('list', PaymentListLocal.as_view(), name='Payment List'),
    path('source', PaymentList.as_view(), name='Payment List'),
]