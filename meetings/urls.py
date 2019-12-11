from . import views
from django.urls import path,include

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:meeting_id>/<str:response>/<str:token>', views.response_invitation, name = 'response_invitation'),
    path('<int:meeting_id>/topic', views.topic, name='topic')
]
