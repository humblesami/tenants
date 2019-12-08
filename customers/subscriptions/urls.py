from django.conf.urls import url
from django.urls import path
from .views import subscribe# SubscriptionForm, SaveRequest,

urlpatterns = [
    # url(r'^(?P<plan_id>\d+)/(?P<request_id>)\d*$', SubscriptionForm.as_view()),
    path('<plan_id>', subscribe),
    path('<plan_id>/', subscribe),
    path('<plan_id>/<token>', subscribe)
    # path('save-request', SaveRequest.as_view(), name='Save Request'),
]