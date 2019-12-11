import os
import sys
import threading
import traceback
from django.core.mail import send_mail
from django.template.loader import render_to_string

class SimpleMailThread(threading.Thread):
    def __init__(self, thread_data):
        #array of emails like [ab@gamil.com, cd@yahoo.com] => its required
        self.recipients = thread_data['audience']

        # First two are required attributes
        self.subject = thread_data.get('subject') or 'Odufax mail'
        self.sender_info = thread_data.get('sender') or 'Odufax'

        self.template_data = thread_data.get('template_data')
        self.template_name = thread_data.get('template_name')
        self.html_message = thread_data.get('html_message') or 'Just an empty mail'

        threading.Thread.__init__(self)

    def run(self):
        try:
            html_message = None
            if self.template_name:
                html_message = render_to_string(self.template_name, self.template_data)
        except:
            produce_exception()
            print('Template could not be fetched')
            pass
        try:
            if not html_message:
                html_message = self.html_message
            send_mail(self.subject, '', self.sender_info, self.recipients, html_message=html_message)
        except:
            produce_exception()

def sample_send_email():
    thread_data = {
        'audience' : ['sami.akram@digitalnet.com']
        'subject': 'Marzi ka',
        'sender': 'Marzi ka',
        'html_message': 'Just marzi ki mail'
    }
    SimpleMailThread(thread_data).start()

def produce_exception(msg=None):
    errorMessage = ''
    if not msg:
        eg = traceback.format_exception(*sys.exc_info())
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