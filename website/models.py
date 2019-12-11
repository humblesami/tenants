from django.db import models
from django.contrib.auth.models import User


class UserAuthToken(models.Model):
    username = models.CharField(max_length=64, null=True)
    token = models.CharField(max_length=32)