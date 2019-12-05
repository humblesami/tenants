from django.urls import path
from .views import AddRequest, CheckName

urlpatterns = [
    path('add-request', AddRequest.as_view(), name='Add Request'),
    path('check-name', CheckName.as_view(), name='Check Name'),
]