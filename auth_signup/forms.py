from allauth.socialaccount.forms import SignupForm as SocialForm
from allauth.account.forms import SignupForm as LocalForm

class AcccountSignupForm(LocalForm):
    _errors = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    def save(self, request):
        user = super().save(request)
        user.username = user.email
        user.save()
        return user


class SocialSignupForm(SocialForm):
    _errors = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    def save(self, request):
        user = super().save(request)
        user.username = user.email
        user.save()
        return user
