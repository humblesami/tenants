from . import views
from django.urls import path,include

urlpatterns = [
    path('get_details', views.get_details, name='get_details'),
    path('get_details_public', views.get_details_public, name='get_details_public'),
    path('sign-doc/<str:token>', views.sign_doc_public, name='sign_doc_public'),
]
