from . import views
from django.urls import path

urlpatterns = [
    path('clear-moved', views.clear_moved, name='clear_moved'),
]
