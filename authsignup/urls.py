from . import views
from django.urls import path,include

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('verify-token', views.verify_token, name='verify_token'),
    path('verify-auth-code', views.load_verify_code_page, name='verify_code'),
    path('reset-password/<str:token>', views.reset_password, name='password_reset'),
    path(r'offline',views.offline_layout, name='offline page'),
    path(r'ping',views.ping, name='Ping'),
]
