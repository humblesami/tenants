import datetime
from django.db import models
from django.contrib.auth.models import User as user_model
from django_currentuser.middleware import get_current_user


class CustomModel(models.Model):
    class Meta:
        abstract = True
    created_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(
        user_model,
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_created_by',
        related_query_name='%(app_label)s_%(class)s'
        )
    updated_at = models.DateTimeField(null=True)
    updated_by = models.ForeignKey(
        user_model,
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_updated_by',
        related_query_name='%(app_label)s_%(class)s'
        )
    
    def save(self, *args, **kwargs):
        req_user = get_current_user()
        if self.pk is None:
            self.created_at = datetime.datetime.now()
            self.created_by = req_user
        else:
            self.updated_at = datetime.datetime.now()
            self.updated_by = req_user
        super(CustomModel, self).save(*args, **kwargs)


