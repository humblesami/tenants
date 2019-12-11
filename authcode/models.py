from django.db import models
from django.conf import settings
import os
import sys
import traceback
import threading
from django.core.mail import send_mail
from django.template.loader import render_to_string


def produce_exception(msg=None):
    if not msg:
        eg = traceback.format_exception(*sys.exc_info())
        errorMessage = ''
        cnt = 0
        for er in eg:
            cnt += 1
            if not 'lib/python' in er:
                errorMessage += " " + er
    else:
        errorMessage = msg
    try:
        dir = os.path.dirname(os.path.realpath(__file__))
        ar = dir.split('/')
        ar = ar[:-1]
        dir = ('/').join(ar)
        with open(dir+'/error_log.txt', "a+") as f:
            f.write(errorMessage + '\n')
    except:
        try:
            dir = os.path.dirname(os.path.realpath(__file__))
            ar = dir.split('\\')
            ar = ar[:-1]
            dir = ('\\').join(ar)
            with open(dir + '\\error_log.txt', "a+") as f:
                f.write(errorMessage + '\n')
        except:
            eg = traceback.format_exception(*sys.exc_info())
            errorMessage = ''
            cnt = 0
            for er in eg:
                cnt += 1
                if not 'lib/python' in er:
                    errorMessage += " " + er
            return errorMessage


class TwoFactorAuthenticate(models.Model):
    code = models.CharField(max_length=10)
    uuid = models.CharField(max_length=10)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    auth_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

def __str__(self):
    return self.code


class ThreadEmail(threading.Thread):
    def __init__(self, thread_data):
        self.subject = thread_data['subject']
        self.emails = thread_data['emails']
        self.template_data = thread_data['template_data']
        self.template_name = thread_data['template_name']
        threading.Thread.__init__(self)


    def run (self):
        try:
            subject = self.subject
            html_message = render_to_string(self.template_name, self.template_data)
            send_mail(self.subject, '', "sami@gmai.com", self.emails, html_message=html_message)
        except:
            produce_exception()
