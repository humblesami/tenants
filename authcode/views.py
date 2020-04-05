import json
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from .models import TwoFactorAuthenticate, ThreadEmail
from signalwire.rest import Client as signalwire_client
from twilio.twiml.messaging_response import Message, MessagingResponse

def generate_code(request):
    req = request.GET
    address = req.get('address')
    auth_type = req.get('auth_type')

    if not auth_type:
        return HttpResponse('Invalid auth type')

    code = get_random_string(length=6)
    uuid = get_random_string(length=10)

    if auth_type == 'email':
        if not address:
            return HttpResponse('Email address not provided for dual factor authentication')
        auth_code_object = TwoFactorAuthenticate(code=code, uuid=uuid, email=address, auth_type=auth_type)
        auth_code_object.save()

        email_data = {}
        email_data['subject'] = 'Two Factor varification'
        email_data['template_data'] = {
            'code': code
        }
        email_data['emails'] = [address]
        email_data['template_name'] = 'code_verification.html'
        ThreadEmail(email_data).start()
    elif auth_type == 'phone':
        try:
            send_sms(code, address)
        except:
            return HttpResponse('sms could not be sent')
        auth_code_object = TwoFactorAuthenticate(code=code, uuid=uuid, phone=address, auth_type=auth_type)
        auth_code_object.save()

    context = {
        'uuid': uuid,
        'status': 'ok',
    }
    context = json.dumps(context)
    return HttpResponse(context)

def send_sms(code, phone):
    phone = phone.strip()
    phone='+'+phone
    client = signalwire_client("def68a3b-3fae-49cc-8e4b-eb8be8c16fd5","PTc6483de7e249e14075792ca6dda9bfd466a922dc5db2def9" , signalwire_space_url= 'odunet.signalwire.com')    
    exception = False
    try:
        message = client.messages.create(from_='+16178128909',body= code ,to=phone)
    except:
        phone = '+16178128909'
        message = client.messages.create(from_='+16178128909', body=code, to=phone)
        exception = True
    if not exception:
        MessageSid = message.sid
        check = client.messages(MessageSid).fetch()
        if check.status == 'delivered':
            return (message.Status.SENT)
        else:
            client.messages.create(from_='+16178128909',body= code ,to='+16178128909')
def verify_code(request):
    req = request.GET
    code = req['code']
    uuid = req['uuid']
    context = 'Invalid code'
    found = TwoFactorAuthenticate.objects.filter(code=code, uuid=uuid)
    if found:
        context = 'ok'
    return HttpResponse(context)

