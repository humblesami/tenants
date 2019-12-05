from django.conf.urls import url
from django.urls import path
from .views import AddRequest, CheckName, PlanDetails

urlpatterns = [
    path('add-request', AddRequest.as_view(), name='Add Request'),
    path('check-name', CheckName.as_view(), name='Check Name'),
    url(r'^plan/(?P<plan_id>\d+)/(?P<request_id>\d+)$', PlanDetails.as_view()),
]