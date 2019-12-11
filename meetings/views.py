import json

from django.http import HttpResponse
from django.shortcuts import render, redirect

from meetings.model_files.topic import Topic
from .model_files.event import Event, STATE_SELECTION
from restoken.models import PostUserToken

def index(request):
    return render(request, 'index.html', context={})

def response_invitation(request, meeting_id, response, token):
    context = {}
    if token:
        user_token = PostUserToken.validate_token(token)
        if not user_token:
            # context['error'] = 'Invalid Token'
            return redirect('/#/feedback/Invalid Token')
        else:
            request.user = user_token.user
            if meeting_id != user_token.post_info.res_id:
                # context['error'] = 'Invalid Token'
                return redirect('/#/feedback/Invalid Token')
            else:
                response_valid = False
                for state in STATE_SELECTION:
                    if state[0] == response:
                        response_valid = True
                        break
                if not response_valid:
                    # context['error'] = 'Invlalid Response'
                    return redirect('/#/feedback/Invalid Token')
                else:
                    params = {
                        'meeting_id': meeting_id,
                        'response': response,
                        'user_id': user_token.user.id
                    }
                    if Event.respond_invitation(request, params) == 'done':
                        # context['success'] = 'Response Submitted Successfully'
                        return redirect('/#/thanks/Thanks Your Answer is Saved Successfully..!')
                    else:
                        # context['error'] = 'Error While Submitting Response'
                        return redirect('/#/feedback/Error While Submitting Response')
    else:
        # context['error'] = 'Invalid Token'
        return redirect('/#/feedback/Invalid Token')
    # return render(request, 'response_submit.html', context)


def topic(request, meeting_id):
    all_topics = []
    if meeting_id:
        topics = Topic.objects.filter(event=meeting_id)
        if topics:
            for topic in topics:
                all_topics.append({'id': topic.id, 'name': topic.name})
        else:
            all_topics.append({'id': '', 'name': '---------'})
    else:
        all_topics.append({'id': '', 'name': '---------'})
    data = {
        'topics': all_topics
    }
    res_data = json.dumps(data)
    return HttpResponse(res_data)

