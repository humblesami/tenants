from django.conf.urls import url
from django.urls import path
from .views import form_company_info, form_payment, form_subscription
from .views import post_payment, post_subscription

urlpatterns = [
    # url(r'^(?P<plan_id>\d+)/(?P<request_id>)\d*$', SubscriptionForm.as_view()),
    path('<plan_id>', form_company_info),

    path('payment/<str:req_token>', form_payment),
    path('post-payment/<req_token>', post_payment),

    path('create/<req_token>', form_subscription),
    path('post-subscription/<req_token>', post_subscription),
]