from . import views
from django.urls import path, include, re_path

urlpatterns = [
    re_path(r'login/?$', views.login_page, name='login'),
    re_path(r'register/?$', views.register_page, name='register'),
    re_path(r'logout/?$', views.logout_user, name='logout'),
    re_path(r'verify-token/?$', views.verify_token, name='verify_token'),
    re_path(r'verify-auth-code/?$', views.load_verify_code_page, name='verify_code'),
    re_path(r'reset-password/<str:token>/?$', views.reset_password, name='password_reset'),
    #tobe changed
    # path(r'offline',views.offline_layout, name='offline page'),
    re_path(r'ping/?$',views.ping, name='Ping'),
]
