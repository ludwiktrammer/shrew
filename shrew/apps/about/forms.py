from django.conf import settings

from contact_form.forms import ReCaptchaContactForm

class ShrewContactForm(ReCaptchaContactForm):
    def from_email(self):
        return 'Code Shrew <{}>'.format(settings.DEFAULT_FROM_EMAIL)

