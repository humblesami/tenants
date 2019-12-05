from django.urls import path
from .views import AddRequest, CheckName, PlanDetails

urlpatterns = [
    path('add-request', AddRequest.as_view(), name='Add Request'),
    path('check-name', CheckName.as_view(), name='Check Name'),
    path('plan/<id>/<request_id>', PlanDetails.as_view(), name='Check Name'),
]