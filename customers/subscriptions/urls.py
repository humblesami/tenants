from django.conf.urls import url
from django.urls import path
from .views import SaveRequest, subscribe# SubscriptionForm

urlpatterns = [
    # url(r'^(?P<plan_id>\d+)/(?P<request_id>)\d*$', SubscriptionForm.as_view()),
    url(r'^(?P<plan_id>\d+)/(?P<request_id>)\d*$', subscribe),
    path('save-request', SaveRequest.as_view(), name='Save Request'),
]