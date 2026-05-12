from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View
from django.views.generic.edit import FormView

from .forms import ShrewContactForm


class AboutView(View):
    def get(self, request):
        context = {
            'contact_form': ShrewContactForm(request=request),
        }

        return render(request, 'about.html', context)


class ContactFormView(FormView):
    """
    Minimal local replacement for the abandoned
    ``django-contact-form-recaptcha`` package's ``ContactFormView``.
    """

    form_class = ShrewContactForm
    template_name = 'contact_form/contact_form.html'
    recipient_list = None

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        if self.recipient_list is not None:
            kwargs['recipient_list'] = self.recipient_list
        return kwargs

    def get_success_url(self):
        return reverse('contact_form_sent')
