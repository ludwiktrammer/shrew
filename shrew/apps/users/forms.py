from django import forms
from django.utils.html import format_html
from django.urls import reverse_lazy

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm

TERMS_LABEL = format_html(
    'I agree to the <a href="{terms}">Terms and Conditions</a> and the <a href="{privacy}">Privacy Policy</a>',
    terms=reverse_lazy('pages:page-detail', kwargs={'slug': 'terms'}),
    privacy=reverse_lazy('pages:page-detail', kwargs={'slug': 'privacy'}),
)
USERNAME_HELP = "The username will be used in the URL of your public profile, so don't use anything personally identifiable."

class ShrewSignupForm(SignupForm):
    terms = forms.BooleanField(
        label=TERMS_LABEL,
    )

    field_order = [
        'email',
        'email2',
        'username',
        'password1',
        'password2',
        'terms',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].help_text = USERNAME_HELP


class ShrewSocialSignupForm(SocialSignupForm):
    terms = forms.BooleanField(
        label=TERMS_LABEL,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].help_text = USERNAME_HELP
