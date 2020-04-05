from . import views
from django.urls import path

urlpatterns = [
    path('submit', views.submit_email, name='drive'),
    path('reset-password', views.reset_password, name='drive'),
]