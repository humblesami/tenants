import os
import json
from django.conf import settings
from django.apps import AppConfig

class AuthSignupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_signup'

    def ready(self):
        pass