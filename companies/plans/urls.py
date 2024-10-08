from django.conf.urls import url
from django.urls import path
from .views import PlanDetails, PlansList

urlpatterns = [
    path('plans', PlansList.as_view()),
    url('plan/<plan_id>', PlanDetails.as_view()),
]