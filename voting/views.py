import sys
import json
import base64
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

from restoken.models import PostUserToken
from .models import Voting, VotingChoice, VotingAnswer


def index(request):
    lastest_voting_list = Voting.objects.all()
    context = {'latest_voting_list': lastest_voting_list}
    return render(request, 'voting/index.html', context)

def detail(request, voting_id):
    voting = Voting.objects.get(pk = voting_id)
    options = list(VotingChoice.objects.filter(voting_type = voting.voting_type_id))
    userInfo = request.user.is_superuser
    context = {
        'voting': voting,
        'options': options,
        'userInfo': userInfo
    }
    return render(request, 'voting/detail.html', context)


def respond(request, voting_id, choice_id, token):
    context = {}
    user_token = None
    user_token = PostUserToken.validate_token(token)
    if not user_token:
        # context['error'] = 'Error: Invalid Token or Expired'
        # return render(request, 'token_submit.html', context)
        return redirect('/#/feedback/Invalid Token or Expired')

    if voting_id != user_token.post_info.res_id:
        return redirect('/#/feedback/Invalid Token or Expired')
        # context['error'] = 'Error: Invalid Token or Expired'
        # return render(request, 'token_submit.html', context)
    voting = Voting.objects.get(id=voting_id)
    if voting.signature_required:
        return respond_with_signature(request, voting, voting_id, choice_id, token)
    if not user_token:
        # context['error'] = 'Error: Invalid Token or Expired'
        return redirect('/#/feedback/Invalid Token or Expired')
        # return render(request, 'token_submit.html', context)
    user_id = user_token.user.id
    choice = voting.voting_type.votingchoice_set.filter(id=choice_id)
    if not choice:
        # context['error'] = 'Error: Invalid voting choice'
        return redirect('/#/feedback/Invalid voting choice')
    else:
        res = None
        if not voting.signature_required:
            res = submit_choice(voting, choice_id, user_id, False)
        if res:
            if res == 'done':
                # context['success'] = 'Response submitted successfully'
                context['voting_id'] = voting_id
                context['choice_id'] = choice_id
                context['token'] = token
                context['signature_required'] = voting.signature_required
            else:
                pass
                # context['error'] = 'Response submitted successfully'
    # return render(request, 'token_submit.html', context)
    return redirect('/#/thanks/Response submitted successfully')

def respond_with_signature(request, voting, voting_id, choice_id, token):
    context = {}
    user_token = None
    voting = Voting.objects.get(id=voting_id)
    context['voting_id'] = voting_id
    context['choice_id'] = choice_id
    context['signature_required'] = voting.signature_required
    user_token = PostUserToken.validate_token(token)
    if not user_token:
        return redirect('/#/feedback/Invalid Token or Expired')
        # context['error'] = 'Invalid Token'
        # return render(request, 'token_submit.html', context)
    context['token'] = token
    # return render(request, 'token_submit.html', context)
    return redirect('/#/thanks/Response submitted successfully')


def answer(request, voting_id):
    user_id=request.user.id
    if not user_id:
        # return HttpResponse('User not found...')
        return redirect('/#/feedback/User not found...')
    if request.method == 'POST':
        choice_id = request.POST.get('answer', False)
        if choice_id:
            choice_id = int(choice_id)
        else:
            # return HttpResponse('Choice Not Found..')
            return redirect('/#/feedback/Choice Not Found...')
        signature_data = request.POST.get('signature_data', False)
        if signature_data:
            signature_data = base64.encodebytes( signature_data.encode())
        try:
            update_Choice(choice_id, voting_id, user_id, signature_data)
            # return HttpResponse('Thanks Your Answer is Updated Successfully..!')
            return redirect('/#/thanks/Thanks Your Answer is Updated Successfully..!')
        except VotingAnswer.DoesNotExist:
            save_Choice(choice_id, voting_id, user_id, signature_data)
            # return HttpResponse('Thanks Your Answer is Saved Successfully..!')
            return redirect('/#/thanks/Thanks Your Answer is Saved Successfully..!')
    else:
        option_id = request.GET.get('answer_id', False)
        signature_data = request.GET.get('signature_data', False)
        if signature_data:
            signature_data = base64.encodebytes( signature_data.encode())
        if option_id:
            try:
                update_Choice(option_id, voting_id, user_id, signature_data)
                # return HttpResponse('Answer Updated Successfully.')
                return redirect('/#/thanks/Thanks Your Answer is Saved Successfully..!')
            except VotingAnswer.DoesNotExist:
                save_Choice(option_id, voting_id, user_id, signature_data)
                # return HttpResponse('Answer Saved Successfully.')
                return redirect('/#/thanks/Thanks Your Answer is Saved Successfully..!')
        else:
            try:

                if voting_id:
                    chart_data = {}
                    voting_choices = list(VotingChoice.objects.filter(voting_type = Voting.objects.get(pk=voting_id).voting_type.id))
                    chart_data['option_data']=[]
                    chart_data['option_results'] = []
                    for option in voting_choices:
                        chart_data['option_data'].append({'id': option.id, 'name': option.name})
                        chart_data['option_results'].append({'option_name': option.name, 'option_result': 0})

                    voting_results = VotingAnswer.objects.values('user_answer__name').filter(voting_id = voting_id).annotate(answer_count=Count('user_answer'))
                    # count = voting_results

                    if voting_results:
                        total = 0
                        for result in voting_results:
                            total += result['answer_count']
                        for result in voting_results:
                            for extra_result in chart_data['option_results']:
                                if extra_result['option_name'] == result['user_answer__name']:
                                    extra_result['option_result'] = result['answer_count']

                voting_answer = VotingAnswer.objects.get(voting_id=voting_id, user_id=request.user.id)
                data = {
                    'answer': voting_answer.user_answer.name,
                    'signature_data': base64.decodestring(voting_answer.signature_data),
                    'chart_data' : chart_data['option_results']
                }
                res_data =json.dumps(data)
                return HttpResponse(res_data)
            except VotingAnswer.DoesNotExist:
                data={
                    'answer': 'nothing'
                }
                res_data = json.dumps(data)
                return HttpResponse(res_data)

def update_my_status(choice_id, voting_id):
    voting_choice = VotingChoice.objects.get(pk=choice_id)
    voting = Voting.objects.get(pk=voting_id)
    voting.my_status = voting_choice.name
    voting.save()

def save_Choice(choice_id, voting_id, user_id, signature_data):
    voting_answer = VotingAnswer()
    voting_answer.user_answer_id = int(choice_id)
    voting_answer.voting_id = voting_id
    voting_answer.user_id = user_id
    if signature_data:
        voting_answer.signature_data = signature_data
    voting_answer.save()
    update_my_status(choice_id, voting_id)

def submit_choice(voting, choice_id, user_id, signature_data=None):
    try:
        if not signature_data:
            if voting.signature_required:
                return 'Error: Signature required to submbit'
        voting_answer = VotingAnswer.objects.filter(voting_id=voting.id, user_id=user_id)
        if not voting_answer:
            voting_answer = VotingAnswer(voting_id=voting.id, user_id=user_id, user_answer_id=choice_id)
        else:
            voting_answer = voting_answer[0]
            voting_answer.user_answer_id = int(choice_id)
        if signature_data:
            voting_answer.signature_data = signature_data
        voting_answer.save()

        return 'done'
    except:
        res = sys.exc_info()
        res = res[1].args[0]
        return res


def update_Choice(choice_id, voting_id, user_id, signature_data):
    try:
        voting_answer = VotingAnswer.objects.get(voting_id=voting_id, user_id=user_id)
        voting_answer.user_answer_id = int(choice_id)
        voting_answer.voting_id = voting_id
        voting_answer.user_id = user_id
        if signature_data:
            voting_answer.signature_data = signature_data
        voting_answer.save()
        update_my_status(choice_id=choice_id, voting_id=voting_id)
    except:
        return sys.exc_info()





