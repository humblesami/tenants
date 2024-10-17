from django.db import models


class TwoFactorAuthenticate(models.Model):
    code = models.CharField(max_length=10)
    uuid = models.CharField(max_length=10)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    auth_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.code
