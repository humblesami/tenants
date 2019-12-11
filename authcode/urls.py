from . import views
from django.urls import path

urlpatterns = [
    path('verify', views.verify_code, name='verify_code'),
    path('generate', views.generate_code, name='generate_code'),
]