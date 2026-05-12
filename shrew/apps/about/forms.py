from django import forms
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.utils.translation import gettext_lazy as _

from captcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    """
    Minimal local replacement for the abandoned ``django-contact-form``
    package. Renders the same templates that used to live under
    ``contact_form/`` so existing templates and URLs keep working.
    """

    name = forms.CharField(max_length=100, label=_('Your name'))
    email = forms.EmailField(max_length=200, label=_('Your email address'))
    title = forms.CharField(max_length=200, label=_('Subject'))
    body = forms.CharField(widget=forms.Textarea, label=_('Your message'))

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [mail_tuple[1] for mail_tuple in settings.MANAGERS]
    subject_template_name = 'contact_form/contact_form_subject.txt'
    template_name = 'contact_form/contact_form.txt'

    def __init__(self, data=None, files=None, request=None,
                 recipient_list=None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        self.request = request
        if recipient_list is not None:
            self.recipient_list = recipient_list
        super().__init__(data=data, files=files, *args, **kwargs)

    def message(self):
        template_name = (
            self.template_name() if callable(self.template_name)
            else self.template_name
        )
        return loader.render_to_string(
            template_name, self.get_context(), request=self.request
        )

    def subject(self):
        template_name = (
            self.subject_template_name() if callable(self.subject_template_name)
            else self.subject_template_name
        )
        subject = loader.render_to_string(
            template_name, self.get_context(), request=self.request
        )
        return ''.join(subject.splitlines())

    def get_context(self):
        if not self.is_valid():
            raise ValueError("Cannot generate Context from invalid contact form")
        return dict(self.cleaned_data, site=get_current_site(self.request))

    def get_message_dict(self):
        if not self.is_valid():
            raise ValueError("Message cannot be sent from invalid contact form")
        message_dict = {}
        for message_part in ('from_email', 'message', 'recipient_list', 'subject'):
            attr = getattr(self, message_part)
            message_dict[message_part] = attr() if callable(attr) else attr
        return message_dict

    def save(self, fail_silently=False):
        send_mail(fail_silently=fail_silently, **self.get_message_dict())


class ReCaptchaContactForm(ContactForm):
    captcha = ReCaptchaField()


class ShrewContactForm(ReCaptchaContactForm):
    def from_email(self):
        return 'Code Shrew <{}>'.format(settings.DEFAULT_FROM_EMAIL)
