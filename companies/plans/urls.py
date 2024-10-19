from django.conf.urls import url
from django.urls import path
from .views import PlansList

urlpatterns = [
    path('plans', PlansList.as_view()),
]