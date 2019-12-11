from django.urls import path

from . import views


app_name = 'voting'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('<int:voting_id>/<int:choice_id>/<str:token>', views.respond, name = 'response'),
    path('<int:voting_id>', views.detail, name = 'detail'),
    path('<int:voting_id>/answer', views.answer, name = 'answer'),
]