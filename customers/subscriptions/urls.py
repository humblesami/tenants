from django.conf.urls import url
from django.urls import path
from .views import subscription_form

urlpatterns = [
    path('<int:plan_id>', subscription_form),
    path('<int:plan_id>/<token>', subscription_form),
    # path('post-form', subscribe),

    # path('<int:plan_id>', form_company_info),
    # path('payment/<req_token>', form_payment),
    # path('post-payment/<req_token>', post_payment),
    #
    # path('create/<req_token>', form_subscription),
    # path('post-subscription/<req_token>', post_subscription),
]